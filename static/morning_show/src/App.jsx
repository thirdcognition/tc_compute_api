import React, { useState, useEffect } from "react";
import {
    BrowserRouter,
    Route,
    Routes,
    Navigate,
    useParams,
    useNavigate,
    useLocation
} from "react-router-dom";
import { Button, Container, Row, Col, ListGroup } from "react-bootstrap";
import LoginForm from "./js/LoginForm.jsx";
import PanelEdit from "./js/PanelEdit.jsx";
import PanelDetails from "./js/PanelDetails.jsx";
import session from "./js/helpers/session.js";
import { fetchPublicPanels } from "./js/helpers/fetch.js";

function App() {
    return (
        <BrowserRouter basename="/morning_show">
            <AppContent />
        </BrowserRouter>
    );
}

function AppContent() {
    const [panels, setPanels] = useState([]);
    const [selectedPanel, setSelectedPanel] = useState("new");
    const [loading, setLoading] = useState(true);

    const navigate = useNavigate();
    const curLocation = useLocation();
    const { id: routeIdFromParams } = useParams();
    const [routeId, setRouteId] = useState(routeIdFromParams);
    const [redirectPath, setRedirectPath] = useState(curLocation.pathname);

    useEffect(() => {
        session.setNavigate(navigate);
    }, [navigate]);

    useEffect(() => {
        if (session.isAuthenticated()) {
            fetchPanels();
        }
        setLoading(false);
    }, []);

    useEffect(() => {
        if (curLocation && curLocation.state && curLocation.state.from) {
            setRedirectPath(curLocation.state.from.pathname);
        }
    }, [curLocation]);

    useEffect(() => {
        const match = curLocation.pathname.match(/^\/panel\/([^/]+)/);
        if (match) {
            setRouteId(match[1]);
        }
    }, [curLocation]);

    useEffect(() => {
        if (!loading && routeId && panels.length > 0) {
            const panel = panels.find((p) => p.id === routeId);
            if (panel) {
                setSelectedPanel(panel);
            }
        }
    }, [loading, routeId, panels]);

    async function fetchPanels() {
        try {
            const panelsData = await fetchPublicPanels();
            const sortedPanels = Array.isArray(panelsData)
                ? panelsData.sort(
                      (a, b) => new Date(b.created_at) - new Date(a.created_at)
                  )
                : [];
            setPanels(sortedPanels);
        } catch (error) {
            console.error("Error fetching panels:", error);
            setPanels([]);
        }
    }

    function handleLogin() {
        fetchPanels();
        navigate(redirectPath);
    }

    function logout() {
        session.logout();
        setPanels([]);
        setSelectedPanel("new");
    }

    const handlePanelChange = (panel) => {
        setSelectedPanel(panel);
        if (panel === "new") {
            setRouteId(null);
            navigate("/new");
        } else if (panel && panel.id) {
            setRouteId(panel.id);
            navigate(`/panel/${panel.id}`);
        }
    };

    if (loading) {
        return null;
    }

    return (
        <Container>
            <Row>
                <Col md={12}>
                    <div className="flex justify-between items-center mb-5 p-2 bg-gray-100 border-b border-gray-300">
                        <h1 className="m-0">My Morning Show</h1>
                        {session.isAuthenticated() && (
                            <Button variant="secondary" onClick={logout}>
                                Logout
                            </Button>
                        )}
                    </div>
                </Col>
            </Row>
            <Row>
                {session.isAuthenticated() && (
                    <Col md={4}>
                        <ListGroup>
                            <ListGroup.Item
                                action
                                active={selectedPanel === "new"}
                                onClick={() => handlePanelChange("new")}
                            >
                                Create show
                            </ListGroup.Item>
                            {panels.map((panel) => (
                                <ListGroup.Item
                                    key={panel.id}
                                    action
                                    active={
                                        selectedPanel &&
                                        selectedPanel.id === panel.id
                                    }
                                    onClick={() => handlePanelChange(panel)}
                                    className={
                                        selectedPanel &&
                                        selectedPanel.id === panel.id
                                            ? "text-white bg-blue-500"
                                            : ""
                                    }
                                >
                                    <div
                                        className={
                                            selectedPanel &&
                                            selectedPanel.id === panel.id
                                                ? "text-white"
                                                : ""
                                        }
                                    >
                                        {panel.title}
                                    </div>
                                    <div
                                        className={
                                            selectedPanel &&
                                            selectedPanel.id === panel.id
                                                ? "text-white text-sm"
                                                : "text-gray-600 text-sm"
                                        }
                                    >
                                        {new Date(
                                            panel.created_at
                                        ).toLocaleString()}
                                    </div>
                                </ListGroup.Item>
                            ))}
                        </ListGroup>
                    </Col>
                )}
                <Col
                    md={session.isAuthenticated() ? 8 : 12}
                    className={
                        !session.isAuthenticated()
                            ? "d-flex justify-content-center"
                            : ""
                    }
                >
                    <Routes>
                        <Route
                            path="/login"
                            element={
                                <React.Fragment>
                                    <div className="max-w-md w-full mx-auto">
                                        <p>
                                            Please log in to access your panels.
                                        </p>
                                        <LoginForm onLogin={handleLogin} />
                                    </div>
                                </React.Fragment>
                            }
                        />
                        <Route
                            path="/new"
                            element={
                                session.isAuthenticated() ? (
                                    <PanelEdit
                                        fetchPanels={fetchPanels}
                                        setSelectedPanel={setSelectedPanel}
                                    />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                        <Route
                            path="/panel/:id/edit"
                            element={
                                session.isAuthenticated() ? (
                                    <PanelEdit
                                        fetchPanels={fetchPanels}
                                        setSelectedPanel={setSelectedPanel}
                                        initialPanelId={routeId}
                                    />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                        <Route
                            path="/panel/:id"
                            element={
                                session.isAuthenticated() ? (
                                    <PanelDetailsWrapper panels={panels} />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                        <Route
                            path="/"
                            element={
                                session.isAuthenticated() ? (
                                    <Navigate to={redirectPath} />
                                ) : (
                                    <Navigate to="/login" />
                                )
                            }
                        />
                    </Routes>
                </Col>
            </Row>
        </Container>
    );
}

function PanelDetailsWrapper({ panels }) {
    const { id } = useParams();
    const panel = panels.find((p) => p.id === id);

    return panel ? <PanelDetails panel={panel} /> : <div>Panel not found</div>;
}

export default App;
