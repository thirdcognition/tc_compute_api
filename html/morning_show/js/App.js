import LoginForm from "./LoginForm.js";
import AddShow from "./AddShow.js";
import PanelDetails from "./PanelDetails.js";

const { useState, useEffect } = React;
const { Form, Button, Container, Row, Col, Card, Accordion, ListGroup } =
    ReactBootstrap;

function App() {
    const [title, setTitle] = useState("");
    const [links, setLinks] = useState([]);
    const [inputText, setInputText] = useState("");
    const [panels, setPanels] = useState([]);
    const [selectedPanel, setSelectedPanel] = useState("new");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [accessToken, setAccessToken] = useState("");

    useEffect(() => {
        const token = getCookie("access_token");
        if (token) {
            setIsLoggedIn(true);
            setAccessToken(token);
            fetchPanels(token);
        }
    }, []);

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(";").shift();
    }

    function setCookie(name, value, days) {
        const d = new Date();
        d.setTime(d.getTime() + days * 24 * 60 * 60 * 1000);
        const expires = "expires=" + d.toUTCString();
        document.cookie = name + "=" + value + ";" + expires + ";path=/";
    }

    async function fetchPanels(accessToken) {
        try {
            const panelsData = await fetchPublicPanels(accessToken);
            setPanels(panelsData);
        } catch (error) {
            console.error("Error fetching panels:", error);
        }
    }

    async function login(event) {
        event.preventDefault();
        try {
            const response = await fetch(
                `http://${window.location.hostname}:4000/auth/login`,
                {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        Accept: "application/json"
                    },
                    body: JSON.stringify({
                        email: email,
                        password: password
                    })
                }
            );
            const data = await response.json();
            setCookie("access_token", data.access_token, 1);
            setIsLoggedIn(true);
            setAccessToken(data.access_token);
            fetchPanels(data.access_token);
        } catch (error) {
            console.error("Error logging in:", error);
        }
    }

    function logout() {
        setCookie("access_token", "", -1);
        setIsLoggedIn(false);
        setPanels([]); // Clear panels on logout
        setSelectedPanel("new"); // Reset selected panel
    }

    async function fetchData(endpoint, accessToken) {
        const response = await fetch(
            `http://${window.location.hostname}:4000${endpoint}`,
            {
                method: "GET",
                headers: {
                    Accept: "application/json",
                    Authorization: `Bearer ${accessToken}`
                }
            }
        );

        if (response.status === 401) {
            logout();
            throw new Error("Unauthorized access - logging out.");
        }

        return response.json();
    }

    async function fetchPublicPanels(accessToken) {
        const [panels, audios, transcripts] = await Promise.all([
            fetchData("/public_panel/discussions/", accessToken),
            fetchData("/public_panel/audios/", accessToken),
            fetchData("/public_panel/transcripts/", accessToken)
        ]);

        const audioMap = audios.reduce((map, audio) => {
            if (!map[audio.public_panel_id]) map[audio.public_panel_id] = [];
            map[audio.public_panel_id].push(audio);
            return map;
        }, {});

        const transcriptMap = transcripts.reduce((map, transcript) => {
            if (!map[transcript.public_panel_id])
                map[transcript.public_panel_id] = [];
            map[transcript.public_panel_id].push(transcript);
            return map;
        }, {});

        return panels.map((panel) => ({
            ...panel,
            audios: audioMap[panel.id] || [],
            transcripts: transcriptMap[panel.id] || []
        }));
    }

    const resetState = () => {
        setTitle("");
        setLinks([]);
        setInputText("");
        // Add any other state variables that need to be reset
    };

    const handlePanelChange = (panel) => {
        resetState();
        setSelectedPanel(panel);
    };

    return React.createElement(
        Container,
        null,
        React.createElement(
            Row,
            null,
            React.createElement(
                Col,
                { md: 12 },
                React.createElement(
                    "div",
                    {
                        className: "header-bar",
                        style: {
                            display: "flex",
                            justifyContent: "space-between",
                            alignItems: "center",
                            marginBottom: "20px",
                            padding: "10px",
                            backgroundColor: "#f8f9fa",
                            borderBottom: "1px solid #dee2e6"
                        }
                    },
                    React.createElement(
                        "h1",
                        { style: { margin: 0 } },
                        "My Morning Show"
                    ),
                    isLoggedIn &&
                        React.createElement(
                            Button,
                            { variant: "secondary", onClick: logout },
                            "Logout"
                        )
                )
            )
        ),
        React.createElement(
            Row,
            null,
            isLoggedIn &&
                React.createElement(
                    Col,
                    { md: 4 },
                    React.createElement(
                        ListGroup,
                        null,
                        React.createElement(
                            ListGroup.Item,
                            {
                                action: true,
                                active: selectedPanel === "new",
                                onClick: () => handlePanelChange("new")
                            },
                            "Create show"
                        ),
                        panels.map((panel) =>
                            React.createElement(
                                ListGroup.Item,
                                {
                                    key: panel.id,
                                    action: true,
                                    active:
                                        selectedPanel &&
                                        selectedPanel.id === panel.id,
                                    onClick: () => handlePanelChange(panel)
                                },
                                React.createElement("div", null, panel.title),
                                React.createElement(
                                    "div",
                                    { className: "text-muted small" },
                                    new Date(panel.created_at).toLocaleString()
                                )
                            )
                        )
                    )
                ),
            React.createElement(
                Col,
                {
                    md: isLoggedIn ? 8 : 12,
                    className: !isLoggedIn
                        ? "d-flex justify-content-center"
                        : ""
                },
                !isLoggedIn
                    ? React.createElement(
                          "div",
                          {
                              style: {
                                  maxWidth: "400px",
                                  width: "100%",
                                  margin: "0 auto"
                              }
                          },
                          React.createElement(
                              "p",
                              null,
                              "Please log in to access your panels."
                          ),
                          React.createElement(LoginForm, {
                              email,
                              setEmail,
                              password,
                              setPassword,
                              login
                          })
                      )
                    : selectedPanel === "new"
                      ? React.createElement(AddShow, {
                            title,
                            setTitle,
                            links,
                            setLinks,
                            inputText,
                            setInputText,
                            accessToken,
                            fetchPanels,
                            setSelectedPanel
                        })
                      : selectedPanel &&
                        React.createElement(PanelDetails, {
                            panel: selectedPanel,
                            accessToken: accessToken
                        })
            )
        )
    );
}

export default App;
