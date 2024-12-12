const { Form, Button } = ReactBootstrap;
const { useState } = React;

function AddShow({
    title,
    setTitle,
    links,
    setLinks,
    inputText,
    setInputText,
    accessToken,
    fetchPanels,
    setSelectedPanel
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

    const handleFormSubmit = async (e) => {
        e.preventDefault();
        const linksArray = linkFields.filter((link) => link.trim() !== "");
        try {
            const response = await fetch(
                `http://${window.location.hostname}:4000/public_panel/`,
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
                        tts_model: "gemini",
                        longform: false,
                        bucket_name: "public_panels"
                    })
                }
            );
            const result = await response.json();
            console.log("Panel created:", result);
            alert("Panel created successfully!");
            fetchPanels(accessToken); // Update panel list after creation
            setSelectedPanel(result); // Automatically switch to the new panel
        } catch (error) {
            console.error("Error:", error);
            alert("Failed to create panel.");
        }
    };

    return React.createElement(
        Form,
        { onSubmit: handleFormSubmit, className: "space-y-4" },
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
            ...linkFields.map((link, index) =>
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
        ),
        React.createElement(
            Button,
            { variant: "primary", type: "submit", className: "w-full py-2" },
            "Submit"
        )
    );
}

export default AddShow;
