#!/bin/bash

SERVER_PORT=${SERVER_PORT:-8080}
FSWATCH_PID=""
UVICORN_PID=""
# Check if running inside Docker
if [ -f /.dockerenv ]; then
    playwright install chromium
    playwright install-deps

    echo "Running inside Docker, starting server without reload."
    uvicorn app.server:app --host 0.0.0.0 --port "$SERVER_PORT" --log-config logging_prod.ini &

    echo "Starting Celery worker"
    celery -A app.core.celery_app worker -B --autoscale=16,4 &

    echo "Starting Flower on port $FLOWER_PORT"
    celery -A app.core.celery_app flower &
else
    # Function to handle cleanup on script exit
    cleanup() {
        echo "Stopping tmux session..."
        if tmux has-session -t server_session 2>/dev/null; then
            tmux kill-session -t server_session
        fi
        if [ -n "$FSWATCH_PID" ] && kill -0 "$FSWATCH_PID" 2>/dev/null; then
            echo "Stopping fswatch process..."
            kill "$FSWATCH_PID"
        fi
        UVICORN_PID=""
        echo "Shutdown complete."
    }

    # Trap SIGINT and SIGTERM and call cleanup()
    trap cleanup SIGINT #SIGTERM

    # Function to display messages in tmux or fallback to console
    display_message() {
        if tmux has-session -t server_session 2>/dev/null; then
            tmux display-message "$1"
        else
            echo "$1"
        fi
    }

    # Function to start tmux session
    start_tmux_session() {
        display_message "Starting tmux session..."
        tmux new-session -s server_session -n uvicorn -d ".venv/bin/uvicorn app.server:app --host 0.0.0.0 --port \"$SERVER_PORT\" --reload --log-config logging.ini"
        # UVICORN_PID=$(pgrep -f "uvicorn app.server:app --host 0.0.0.0 --port $SERVER_PORT")
        tmux select-pane -T uvicorn
        # if [ -z "$UVICORN_PID" ]; then
        #     tmux display-message "Failed to retrieve uvicorn PID. Exiting..."
        #     cleanup
        #     exit 1
        # fi
        tmux split-window -v -t server_session:0 ".venv/bin/celery -A app.core.celery_app worker -B --autoscale=64,8"
        tmux select-pane -T celery_worker
        tmux split-window -v -t server_session:0 ".venv/bin/celery -A app.core.celery_app flower"
        tmux select-pane -T flower

        # Log pane details for debugging
        tmux list-panes -t server_session > /tmp/tmux_panes_creation.log

        # Enable pane titles in the border
        tmux set-option -g pane-border-status top
        tmux set-option -g pane-border-format "#{pane_index} #{pane_title}"
    }

    # Monitor files for changes and restart tmux session
    # monitor_celery_files() {
    #     fswatch -o app source | while read; do
    #         display_message "File changes detected. Restarting tmux session..."
    #         if tmux has-session -t server_session 2>/dev/null; then
    #             tmux kill-session -t server_session
    #             while tmux has-session -t server_session 2>/dev/null; do
    #                 sleep 1
    #             done
    #         fi
    #         start_tmux_session  # Restart the tmux session
    #     done &
    #     FSWATCH_PID=$!
    # }

    # Monitor the main process (uvicorn) and trigger cleanup if it is killed
    monitor_main_process() {
        UVICORN_PID=$(pgrep -f "uvicorn app.server:app --host 0.0.0.0 --port $SERVER_PORT")
        if [ -z "$UVICORN_PID" ]; then
            tmux display-message "Failed to retrieve uvicorn PID. Exiting..."
        fi
        while kill -0 "$UVICORN_PID" 2>/dev/null; do
            sleep 1
        done
        display_message "Main process (uvicorn) terminated. Triggering cleanup..."
        cleanup
    }

    # Set tmux hooks to trigger cleanup if any pane is closed
    setup_tmux_hooks() {
        if tmux has-session -t server_session 2>/dev/null; then
            tmux set-option -g remain-on-exit on
            tmux set-hook -g pane-died "run-shell 'tmux kill-session -t server_session && cleanup'"
        fi
    }



    if ! docker inspect tc-redis &> /dev/null; then
        display_message "tc-redis not found, starting Redis container..."
        docker run --name tc-redis -d -p 6379:6379 redis
    fi

    docker start tc-redis

    .venv/bin/playwright install chromium
    .venv/bin/playwright install-deps

    source .env

    display_message "Not running inside Docker, starting server with reload in tmux session."

    start_tmux_session  # Start the tmux session

    # Monitor celery files for changes
    # monitor_celery_files

    # Set tmux hooks
    setup_tmux_hooks

    # Attach to the tmux session to make it visible
    tmux select-layout -t server_session even-vertical
    tmux attach-session -t server_session

    # Monitor the main process
    monitor_main_process &

fi
