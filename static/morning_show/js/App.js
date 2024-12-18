import LoginForm from "./LoginForm.js";
import PanelEdit from "./PanelEdit.js";
import PanelDetails from "./PanelDetails.js";
const {
    BrowserRouter,
    Route,
    Switch,
    Redirect,
    useParams,
    useHistory,
    useLocation
} = ReactRouterDOM;

const { useState, useEffect } = React;
const { Form, Button, Container, Row, Col, Card, Accordion, ListGroup } =
    ReactBootstrap;

function App() {
    return React.createElement(
        BrowserRouter,
        { basename: "/morning_show" },
        React.createElement(AppContent)
    );
}

function AppContent() {
    const [title, setTitle] = useState("");
    const [links, setLinks] = useState([]);
    const [inputText, setInputText] = useState("");
    const [panels, setPanels] = useState([]);
    const [selectedPanel, setSelectedPanel] = useState("new");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [accessToken, setAccessToken] = useState("");
    const [loading, setLoading] = useState(true);

    const history = useHistory();
    const curLocation = useLocation();
    const { id: routeIdFromParams } = useParams(); // Get the route ID from params
    const [routeId, setRouteId] = useState(routeIdFromParams); // State for routeId
    const [redirectPath, setRedirectPath] = useState(curLocation.pathname);

    console.log("routeId", routeId);

    useEffect(() => {
        const token = getCookie("access_token");
        if (token) {
            setAccessToken(token);
            fetchPanels(token);
        }
        setLoading(false);
        console.log("Token found:", token);
    }, []);

    useEffect(() => {
        if (curLocation && curLocation.state && curLocation.state.from) {
            setRedirectPath(curLocation.state.from.pathname);
        }
        console.log("Current location:", curLocation.pathname);
        console.log("Redirect path set to:", redirectPath);
    }, [curLocation]);

    // Manually set routeId based on location path
    useEffect(() => {
        const match = curLocation.pathname.match(/^\/panel\/([^/]+)/);
        if (match) {
            setRouteId(match[1]);
        }
    }, [curLocation]);

    // New useEffect to set selectedPanel based on route ID
    useEffect(() => {
        if (!loading && routeId && panels.length > 0) {
            const panel = panels.find((p) => p.id === routeId);
            if (panel) {
                setSelectedPanel(panel);
            }
        }
    }, [loading, routeId, panels]);

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
            setPanels(Array.isArray(panelsData) ? panelsData : []);
        } catch (error) {
            console.error("Error fetching panels:", error);
            setPanels([]);
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
            setAccessToken(data.access_token);
            fetchPanels(data.access_token);
            history.push(redirectPath);
        } catch (error) {
            console.error("Error logging in:", error);
        }
    }

    function logout() {
        setCookie("access_token", "", -1);
        setPanels([]);
        setSelectedPanel("new");
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

        if (response.status === 401 || response.status === 403) {
            history.push("/login");
            throw new Error("Unauthorized access - redirecting to login.");
        }

        return response.json();
    }

    async function fetchPublicPanels(accessToken) {
        const panels = await fetchData(
            "/public_panel/discussions/",
            accessToken
        );
        return Array.isArray(panels) ? panels : [];
    }

    const resetState = () => {
        setTitle("");
        setLinks([]);
        setInputText("");
    };

    const handlePanelChange = (panel) => {
        resetState();
        setSelectedPanel(panel);
        if (panel === "new") {
            history.push("/new");
        } else if (panel && panel.id) {
            history.push(`/panel/${panel.id}`);
        }
    };

    if (loading) {
        return null;
    }

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
                    accessToken &&
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
            accessToken &&
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
                                    onClick: () => handlePanelChange(panel),
                                    style: {
                                        color:
                                            selectedPanel &&
                                            selectedPanel.id === panel.id
                                                ? "#fff"
                                                : "",
                                        backgroundColor:
                                            selectedPanel &&
                                            selectedPanel.id === panel.id
                                                ? "#007bff"
                                                : ""
                                    }
                                },
                                React.createElement("div", null, panel.title),
                                React.createElement(
                                    "div",
                                    {
                                        style: {
                                            color:
                                                selectedPanel &&
                                                selectedPanel.id === panel.id
                                                    ? "#fff"
                                                    : "#6c757d",
                                            fontSize: "0.8em"
                                        }
                                    },
                                    new Date(panel.created_at).toLocaleString()
                                )
                            )
                        )
                    )
                ),
            React.createElement(
                Col,
                {
                    md: accessToken ? 8 : 12,
                    className: !accessToken
                        ? "d-flex justify-content-center"
                        : ""
                },
                React.createElement(
                    Switch,
                    null,
                    React.createElement(
                        Route,
                        { path: "/login" },
                        React.createElement(
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
                    ),
                    React.createElement(
                        Route,
                        { path: "/new" },
                        accessToken
                            ? React.createElement(PanelEdit, {
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
                            : React.createElement(Redirect, { to: "/login" })
                    ),
                    React.createElement(
                        Route,
                        { path: "/panel/:id" },
                        accessToken
                            ? React.createElement(PanelDetailsWrapper, {
                                  panels,
                                  accessToken
                              })
                            : React.createElement(Redirect, { to: "/login" })
                    ),
                    React.createElement(
                        Route,
                        { path: "/panel/:id/edit" }, // New route for editing
                        accessToken
                            ? React.createElement(PanelEdit, {
                                  title,
                                  setTitle,
                                  links,
                                  setLinks,
                                  inputText,
                                  setInputText,
                                  accessToken,
                                  fetchPanels,
                                  setSelectedPanel,
                                  initialPanelId: routeId // Pass the panelId
                              })
                            : React.createElement(Redirect, { to: "/login" })
                    ),
                    React.createElement(
                        Route,
                        { path: "/", exact: true },
                        accessToken
                            ? React.createElement(Redirect, {
                                  to: redirectPath
                              })
                            : React.createElement(Redirect, { to: "/login" })
                    )
                )
            )
        )
    );
}

function PanelDetailsWrapper({ panels, accessToken }) {
    const { id } = useParams();
    const panel = panels.find((p) => p.id === id);

    return panel
        ? React.createElement(PanelDetails, { panel, accessToken })
        : React.createElement("div", null, "Panel not found");
}

export default App;
