import { Form, Button } from "react-bootstrap";
import session from "./helpers/session.js";
import { useState } from "react";

function LoginForm({ onLogin }) {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");

    async function login(event) {
        event.preventDefault();
        try {
            await session.login(email, password);
            onLogin();
        } catch (error) {
            console.error("Error logging in:", error);
        }
    }
    return (
        <Form onSubmit={login} className="space-y-4">
            <Form.Group controlId="email">
                <Form.Label className="font-semibold">Email:</Form.Label>
                <Form.Control
                    type="email"
                    placeholder="Enter email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
            </Form.Group>
            <Form.Group controlId="password">
                <Form.Label className="font-semibold">Password:</Form.Label>
                <Form.Control
                    type="password"
                    placeholder="Enter password"
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                />
            </Form.Group>
            <Button variant="primary" type="submit" className="w-full py-2">
                Login
            </Button>
        </Form>
    );
}

export default LoginForm;
