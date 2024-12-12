const { Form, Button } = ReactBootstrap;

function LoginForm({ email, setEmail, password, setPassword, login }) {
    return React.createElement(
        Form,
        { onSubmit: login, className: "space-y-4" },
        React.createElement(
            Form.Group,
            { controlId: "email" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Email:"
            ),
            React.createElement(Form.Control, {
                type: "email",
                placeholder: "Enter email",
                value: email,
                onChange: (e) => setEmail(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        ),
        React.createElement(
            Form.Group,
            { controlId: "password" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Password:"
            ),
            React.createElement(Form.Control, {
                type: "password",
                placeholder: "Enter password",
                value: password,
                onChange: (e) => setPassword(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        ),
        React.createElement(
            Button,
            { variant: "primary", type: "submit", className: "w-full py-2" },
            "Login"
        )
    );
}

export default LoginForm;
