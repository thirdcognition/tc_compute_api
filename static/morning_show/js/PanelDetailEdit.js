const { useState } = React;
const { Form, Button } = ReactBootstrap;

function PanelDetailEdit({
    title,
    setTitle,
    links,
    setLinks,
    inputText,
    setInputText
}) {
    const [linkFields, setLinkFields] = useState(links);

    const handleLinkChange = (index, value) => {
        const newLinkFields = [...linkFields];
        newLinkFields[index] = value;
        setLinkFields(newLinkFields);
        setLinks(newLinkFields);
    };

    const addLinkField = () => {
        setLinkFields([...linkFields, ""]);
    };

    return React.createElement(
        React.Fragment,
        null,
        React.createElement(
            Form.Group,
            { controlId: "title" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Title:"
            ),
            React.createElement(Form.Control, {
                type: "text",
                placeholder: "Enter title here...",
                value: title,
                onChange: (e) => setTitle(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        ),
        React.createElement(
            Form.Group,
            { controlId: "links" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Paste your links (one per line):"
            ),
            linkFields.map((link, index) =>
                React.createElement(Form.Control, {
                    key: index,
                    type: "text",
                    placeholder: "Enter URL here...",
                    value: link,
                    onChange: (e) => handleLinkChange(index, e.target.value),
                    style: { marginBottom: "10px" },
                    className:
                        "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
                })
            ),
            React.createElement(
                Button,
                {
                    variant: "secondary",
                    type: "button",
                    onClick: addLinkField,
                    style: { width: "100%", marginBottom: "10px" },
                    className: "py-2"
                },
                "+ Add another link"
            )
        ),
        React.createElement(
            Form.Group,
            { controlId: "inputText" },
            React.createElement(
                Form.Label,
                { className: "font-semibold" },
                "Input Text:"
            ),
            React.createElement(Form.Control, {
                as: "textarea",
                rows: 5,
                placeholder: "Enter text here...",
                value: inputText,
                onChange: (e) => setInputText(e.target.value),
                className:
                    "border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50"
            })
        )
    );
}

export default PanelDetailEdit;
