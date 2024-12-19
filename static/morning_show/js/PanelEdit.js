const { Form, Button, Spinner } = ReactBootstrap;
const { useState, useEffect } = React;
const { Redirect } = ReactRouterDOM; // Import Link
import PanelDetailEdit from "./PanelDetailEdit.js";
import PanelDetailDisplay from "./PanelDetailDisplay.js";
import TranscriptDetailEdit from "./TranscriptDetailEdit.js";
import TranscriptDetailDisplay from "./TranscriptDetailDisplay.js";
import AudioDetailEdit from "./AudioDetailEdit.js";
import { defaultTtsModelOptions } from "./options.js";

function PanelEdit({
    accessToken,
    fetchPanels,
    setSelectedPanel,
    initialPanelId // PanelId might be passed as a parameter
}) {
    const [title, setTitle] = useState("");
    const [links, setLinks] = useState([]);
    const [googleNewsConfigs, setGoogleNewsConfigs] = useState([]);
    const [inputText, setInputText] = useState("");
    const [linkFields, setLinkFields] = useState(links);
    const [newsConfigFields, setNewsConfigFields] = useState(googleNewsConfigs);
    const [taskId, setTaskId] = useState(null);
    const [taskStatus, setTaskStatus] = useState("idle"); // Initialize to "idle"
    const [isPolling, setIsPolling] = useState(false);
    const [existingTranscript, setExistingTranscript] = useState(null);
    const [existingAudio, setExistingAudio] = useState(null);
    const [transcriptId, setTranscriptId] = useState(null); // New state for transcriptId
    const [panelId, setPanelId] = useState(initialPanelId || null); // Manage panelId internally
    const [transcriptCreated, setTranscriptCreated] = useState(false);
    const [redirectToPanel, setRedirectToPanel] = useState(false); // New state for redirection
    const [longForm, setLongForm] = useState(true); // New state for longForm

    // New state variables for storing fetched data
    const [discussionData, setDiscussionData] = useState(null);
    const [transcriptData, setTranscriptData] = useState(null);
    const [transcriptUrls, setTranscriptUrls] = useState({});
    const [audioUrls, setAudioUrls] = useState({});

    // Updated state variables for conversation config
    const [wordCount, setWordCount] = useState(200);
    const [creativity, setCreativity] = useState(1);
    const [conversationStyle, setConversationStyle] = useState([
        "engaging",
        "fast-paced",
        "enthusiastic"
    ]);
    const [rolesPerson1, setRolesPerson1] = useState("main summarizer");
    const [rolesPerson2, setRolesPerson2] = useState("questioner/clarifier");
    const [dialogueStructure, setDialogueStructure] = useState([
        "Introduction",
        "Main Content Summary",
        "Conclusion"
    ]);
    const [engagementTechniques, setEngagementTechniques] = useState([
        "rhetorical questions",
        "anecdotes",
        "analogies",
        "humor"
    ]);
    const [userInstructions, setUserInstructions] = useState("");
    const [ttsModel, setTtsModel] = useState("elevenlabs");
    const [defaultVoiceQuestion, setDefaultVoiceQuestion] = useState("");
    const [defaultVoiceAnswer, setDefaultVoiceAnswer] = useState("");
    const [outputLanguage, setOutputLanguage] = useState("English");

    useEffect(() => {
        const selectedModel = defaultTtsModelOptions.find(
            (model) => model.value === ttsModel
        );
        if (selectedModel) {
            setDefaultVoiceQuestion(selectedModel.defaultVoices.question);
            setDefaultVoiceAnswer(selectedModel.defaultVoices.answer);
        }
    }, [ttsModel]);

    useEffect(() => {
        if (initialPanelId) {
            setPanelId(initialPanelId);
        } else {
            setPanelId(null); // Reset panelId for new panels
            setTranscriptId(null); // Reset transcriptId for new panels
            setTranscriptData(null); // Reset transcriptData for new panels
            setTranscriptCreated(null);
        }
    }, [initialPanelId]);

    useEffect(() => {
        if (panelId) {
            refreshPanelData(panelId);
        }
    }, [panelId, accessToken]);

    useEffect(() => {
        if (transcriptData && transcriptData.length === 1) {
            setTranscriptId(transcriptData[0].id);
        }
    }, [transcriptData]);

    const refreshPanelData = async (panelId) => {
        try {
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port ? `:${window.location.port}` : "";

            // Fetch updated discussion data
            const discussionResponse = await fetch(
                `${protocol}//${host}${port}/public_panel/${panelId}`,
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
            const discussionData = await discussionResponse.json();
            setDiscussionData(discussionData); // Save discussion data to state
            setTitle(discussionData.title);
            if (discussionData.metadata) {
                setInputText(discussionData.metadata.input_text);
                setLinkFields(discussionData.metadata.input_source);
                setGoogleNewsConfigs(discussionData.metadata.google_news || []); // Update googleNewsConfigs
            }

            // Fetch updated transcripts
            const transcriptResponse = await fetch(
                `${protocol}//${host}${port}/public_panel/${panelId}/transcripts`,
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
            const transcriptData = await transcriptResponse.json();
            if (transcriptData.length > 0) {
                setTranscriptCreated(true);
                setTranscriptData(transcriptData); // Save transcript data to state
                setExistingTranscript(transcriptData);
            }

            // Fetch updated audios
            const audioResponse = await fetch(
                `${protocol}//${host}${port}/public_panel/${panelId}/audios`,
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
            const audioData = await audioResponse.json();
            setExistingAudio(audioData);

            // Fetch files for transcript and audio URLs
            const filesResponse = await fetch(
                `/public_panel/${panelId}/files`,
                {
                    headers: {
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
            const filesData = await filesResponse.json();
            const updatedTranscriptUrls = filesData.transcript_urls
                ? Object.fromEntries(
                      Object.entries(filesData.transcript_urls).map(
                          ([id, url]) => [
                              id,
                              url.replace(
                                  "http://127.0.0.1:4000",
                                  `${protocol}//${host}${port}`
                              )
                          ]
                      )
                  )
                : {};
            const updatedAudioUrls = filesData.audio_urls
                ? Object.fromEntries(
                      Object.entries(filesData.audio_urls).map(([id, url]) => [
                          id,
                          url.replace(
                              "http://127.0.0.1:4000",
                              `${protocol}//${host}${port}`
                          )
                      ])
                  )
                : {};
            setTranscriptUrls(updatedTranscriptUrls);
            setAudioUrls(updatedAudioUrls);
        } catch (error) {
            console.error("Error refreshing panel data:", error);
        }
    };

    const handleLinkChange = (index, value) => {
        const newLinkFields = [...linkFields];
        newLinkFields[index] = value;
        setLinkFields(newLinkFields);
        setLinks(newLinkFields);
    };

    const handleNewsConfigChange = (index, key, value) => {
        const newNewsConfigFields = [...newsConfigFields];
        if (!newNewsConfigFields[index]) {
            newNewsConfigFields[index] = {};
        }
        newNewsConfigFields[index][key] = value;
        setNewsConfigFields(newNewsConfigFields);
        setGoogleNewsConfigs(newNewsConfigFields);
    };

    const addLinkField = () => {
        setLinkFields([...linkFields, ""]);
    };

    const addNewsConfigField = () => {
        setNewsConfigFields([...newsConfigFields, {}]);
    };

    const pollTaskStatus = async (id, type) => {
        try {
            setIsPolling(true);
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port ? `:${window.location.port}` : "";
            const response = await fetch(
                `${protocol}//${host}${port}/system/task_status/${id}`,
                {
                    method: "GET",
                    headers: {
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    }
                }
            );
            const result = await response.json();
            setTaskStatus(result.status);
            if (result.status.toLowerCase() === "success") {
                fetchPanels(accessToken);
                refreshPanelData(panelId); // Refresh panel data to fetch transcriptId
                setIsPolling(false);
                setTaskStatus("idle"); // Reset to "idle" after success
            } else if (result.status.toLowerCase() === "failure") {
                setIsPolling(false);
                setTaskStatus("idle"); // Reset to "idle" after failure
            } else {
                setTimeout(() => pollTaskStatus(id, type), 5000);
            }
        } catch (error) {
            console.error("Error polling task status:", error);
            setIsPolling(false);
            setTaskStatus("idle"); // Reset to "idle" on error
        }
    };

    const createPanel = async () => {
        const linksArray = links.filter((link) => link.trim() !== "");
        const googleNewsArray = googleNewsConfigs.filter(
            (config) => Object.keys(config).length > 0
        );
        try {
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port ? `:${window.location.port}` : "";
            const response = await fetch(
                `${protocol}//${host}${port}/public_panel/discussion`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        title: title,
                        input_text: inputText,
                        input_source: linksArray,
                        google_news: googleNewsArray,
                        longform: longForm // Include longForm in the request
                    })
                }
            );
            const result = await response.json();
            setSelectedPanel(result.panel_id); // Set the selected panel
            setPanelId(result.panel_id); // Ensure panelId is set
            refreshPanelData(result.panel_id);
            fetchPanels(accessToken); // Refresh panel data in App.js
            setRedirectToPanel(true); // Set redirect after panel creation
            return result.panel_id;
        } catch (error) {
            console.error("Error creating panel:", error);
            alert("Failed to create panel.");
            return null;
        }
    };

    const createTranscript = async (panelId) => {
        const linksArray = links.filter((link) => link.trim() !== "");
        const googleNewsArray =
            googleNewsConfigs.length > 0
                ? googleNewsConfigs
                : discussionData
                  ? discussionData.metadata.google_news
                  : [];
        const articleCount = Math.max(
            (googleNewsArray.reduce(
                (val, config) => val + config.articles,
                0
            ) || 0) + (linksArray || []).length,
            1
        );
        const maxNumChunks = Math.max(
            Math.ceil((wordCount * 5) / 8192),
            articleCount
        );
        const minChunkSize = Math.max(
            Math.min(300, wordCount),
            Math.floor(wordCount / articleCount)
        );
        const targetWordCount =
            (wordCount / articleCount) * 3 < 8192
                ? wordCount / articleCount
                : Math.ceil(8192 / 3);
        try {
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port ? `:${window.location.port}` : "";
            const response = await fetch(
                `${protocol}//${host}${port}/public_panel/transcript`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        title: title,
                        input_source: linksArray,
                        input_text: inputText,
                        conversation_config: {
                            word_count: wordCount,
                            creativity: creativity,
                            conversation_style: conversationStyle,
                            roles_person1: rolesPerson1,
                            roles_person2: rolesPerson2,
                            dialogue_structure: dialogueStructure,
                            engagement_techniques: engagementTechniques,
                            user_instructions:
                                `Use up to ${targetWordCount} words when generating the response. Make sure to fit your response into ${targetWordCount} words! ` +
                                (outputLanguage !== "English"
                                    ? " Make sure to write numbers as text in the specified language. So e.g. in English 10 in is ten, and 0.1 is zero point one."
                                    : "") +
                                userInstructions,
                            output_language: outputLanguage,
                            max_num_chunks: maxNumChunks,
                            min_chunk_size: minChunkSize
                        },
                        max_output_tokens: Math.min(wordCount * 5, 8192),
                        longform: longForm, // Include longForm in the request
                        bucket_name: "public_panels",
                        panel_id: panelId
                    })
                }
            );
            const result = await response.json();
            setTaskId(result.task_id);
            setTranscriptCreated(true);
            setTimeout(() => {
                pollTaskStatus(result.task_id, "transcript");
            }, 1000);
            return result.transcript_id;
        } catch (error) {
            console.error("Error creating transcript:", error);
            alert("Failed to create transcript.");
            return null;
        }
    };

    const createAudio = async (panelId, transcriptId) => {
        const linksArray = links.filter((link) => link.trim() !== "");
        try {
            const protocol = window.location.protocol;
            const host = window.location.hostname;
            const port = window.location.port ? `:${window.location.port}` : "";
            const response = await fetch(
                `${protocol}//${host}${port}/public_panel/audio`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json",
                        Authorization: `Bearer ${accessToken}`
                    },
                    body: JSON.stringify({
                        title: title,
                        tts_model: ttsModel,
                        conversation_config: {
                            text_to_speech: {
                                elevenlabs: {
                                    default_voices: {
                                        question: defaultVoiceQuestion,
                                        answer: defaultVoiceAnswer
                                    },
                                    model: "eleven_multilingual_v2"
                                },
                                gemini: {
                                    default_voices: {
                                        question: defaultVoiceQuestion,
                                        answer: defaultVoiceAnswer
                                    }
                                }
                            }
                        },
                        bucket_name: "public_panels",
                        panel_id: panelId,
                        transcript_id: transcriptId
                    })
                }
            );
            const result = await response.json();
            setTaskId(result.task_id);
            setTimeout(() => {
                pollTaskStatus(result.task_id, "audio");
            }, 1000);
            // setRedirectToPanel(false); // Set redirect after audio creation
        } catch (error) {
            console.error("Error creating audio.", error);
            alert("Failed to create audio.");
        }
    };

    const handlePanelSubmit = async (e) => {
        e.preventDefault();
        const panelId = await createPanel();
        if (panelId) {
            refreshPanelData(panelId);
        }
    };

    const handleTranscriptSubmit = async (e) => {
        e.preventDefault();
        if (panelId) {
            // Ensure panelId is checked
            const transcriptId = await createTranscript(panelId);
            if (transcriptId) {
                refreshPanelData(panelId);
            }
        }
    };

    const handleAudioSubmit = async (e) => {
        e.preventDefault();
        if (panelId && transcriptId) {
            // Ensure transcriptId is used
            await createAudio(panelId, transcriptId);
            refreshPanelData(panelId);
        }
    };

    const getStatusBarStyle = () => {
        switch (taskStatus.toLowerCase()) {
            case "success":
                return "bg-green-500";
            case "failure":
                return "bg-red-500";
            case "idle":
                return "bg-gray-300";
            default:
                return "bg-yellow-500"; // For any other status
        }
    };

    const getStatusSymbol = () => {
        switch (taskStatus.toLowerCase()) {
            case "success":
                return "✔️"; // UML symbol for success
            case "failure":
                return "❌"; // UML symbol for failure
            case "idle":
                return ""; // UML symbol for ok state
            default:
                return ""; // No symbol for other statuses
        }
    };

    if (redirectToPanel) {
        return React.createElement(Redirect, { to: `/panel/${panelId}` });
    }

    return React.createElement(
        "div",
        { className: "space-y-4" },

        React.createElement(
            "div",
            { className: `status-bar p-2 text-white ${getStatusBarStyle()}` },
            React.createElement(
                "div",
                { className: "flex items-center justify-center" },
                isPolling &&
                    React.createElement(
                        Spinner,
                        {
                            animation: "border",
                            role: "status",
                            className: "mr-2"
                        },
                        React.createElement(
                            "span",
                            { className: "sr-only" },
                            "Building..."
                        )
                    ),
                React.createElement(
                    "div",
                    { className: "status-text" },
                    `${getStatusSymbol()} Status: ${taskStatus}`
                )
            )
        ),
        !panelId &&
            React.createElement(
                "div",
                { className: "panel-container border p-3 mb-4 rounded" },
                React.createElement(
                    "h3",
                    { className: "font-bold mb-3" },
                    "Create Panel"
                ),
                React.createElement(
                    Form,
                    { onSubmit: handlePanelSubmit },
                    React.createElement(PanelDetailEdit, {
                        title,
                        setTitle,
                        links,
                        setLinks,
                        googleNewsConfigs,
                        setGoogleNewsConfigs,
                        inputText,
                        setInputText
                    }),
                    React.createElement(
                        Button,
                        {
                            variant: "primary",
                            type: "submit",
                            className: "w-full py-2",
                            disabled:
                                taskStatus === "idle"
                                    ? false
                                    : taskStatus !== "failure" &&
                                      taskStatus !== "success"
                        },
                        "Create Panel"
                    )
                )
            ),
        panelId &&
            discussionData &&
            React.createElement(PanelDetailDisplay, {
                panel: discussionData // Pass the entire discussionData
            }),
        transcriptData &&
            transcriptData.map((transcript) =>
                React.createElement(TranscriptDetailDisplay, {
                    transcript: transcript, // Pass the entire transcriptData
                    accessToken,
                    transcriptUrls,
                    existingAudio,
                    audioUrls
                })
            ),
        taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure"
            ? null
            : React.createElement(
                  "div",
                  {
                      className: `transcript-edit-container border p-3 mb-4 rounded`
                  },
                  React.createElement(
                      "h3",
                      { className: "font-bold mb-3" },
                      "Create new Transcript"
                  ),
                  React.createElement(
                      Form,
                      { onSubmit: handleTranscriptSubmit },
                      React.createElement(TranscriptDetailEdit, {
                          wordCount,
                          setWordCount,
                          creativity,
                          setCreativity,
                          conversationStyle,
                          setConversationStyle,
                          rolesPerson1,
                          setRolesPerson1,
                          rolesPerson2,
                          setRolesPerson2,
                          dialogueStructure,
                          setDialogueStructure,
                          engagementTechniques,
                          setEngagementTechniques,
                          userInstructions,
                          setUserInstructions,
                          outputLanguage,
                          setOutputLanguage,
                          longForm,
                          setLongForm
                      }),
                      React.createElement(
                          Button,
                          {
                              variant: "primary",
                              type: "submit",
                              className: "w-full py-2 mt-3",
                              disabled:
                                  !panelId ||
                                  (taskStatus !== "idle" &&
                                      taskStatus !== "failure" &&
                                      taskStatus !== "success") // Disable if panelId is not defined
                          },
                          "Create Transcript"
                      )
                  )
              ),
        taskStatus !== "idle" &&
            taskStatus !== "success" &&
            taskStatus !== "failure"
            ? React.createElement(
                  "div",
                  {
                      className: "processing-container border p-3 mb-4 rounded"
                  },
                  React.createElement(
                      "h3",
                      { className: "font-bold mb-3" },
                      "Processing..."
                  ),
                  React.createElement(
                      "p",
                      null,
                      "Please wait while the task is being processed."
                  )
              )
            : React.createElement(
                  "div",
                  { className: "audio-container border p-3 mb-4 rounded" },
                  React.createElement(
                      "h3",
                      { className: "font-bold mb-3" },
                      "Create Audio"
                  ),
                  React.createElement(
                      Form,
                      { onSubmit: handleAudioSubmit }, // Ensure this is linked to handleAudioSubmit
                      React.createElement(
                          "div",
                          { className: "mt-3" },
                          transcriptData &&
                              transcriptData.length > 1 &&
                              React.createElement(
                                  "label",
                                  { htmlFor: "transcriptSelect" },
                                  "Select Transcript"
                              ),
                          transcriptData &&
                              transcriptData.length > 1 &&
                              React.createElement(
                                  "select",
                                  {
                                      id: "transcriptSelect",
                                      value: transcriptId || "",
                                      onChange: (e) =>
                                          setTranscriptId(e.target.value),
                                      className: "form-select"
                                  },
                                  transcriptData.map((transcript) =>
                                      React.createElement(
                                          "option",
                                          {
                                              key: transcript.id,
                                              value: transcript.id
                                          },
                                          transcript.title
                                      )
                                  )
                              )
                      ),
                      React.createElement(AudioDetailEdit, {
                          ttsModel,
                          setTtsModel,
                          defaultVoiceQuestion,
                          setDefaultVoiceQuestion,
                          defaultVoiceAnswer,
                          setDefaultVoiceAnswer
                      }),

                      React.createElement(
                          Button,
                          {
                              variant: "primary",
                              type: "submit",
                              className: "w-full py-2 mt-3",
                              disabled:
                                  !transcriptData ||
                                  (taskStatus !== "idle" &&
                                      taskStatus !== "failure" &&
                                      taskStatus !== "success") // Disable if transcriptId is not defined
                          },
                          "Create Audio"
                      )
                  )
              )
    );
}

export default PanelEdit;
