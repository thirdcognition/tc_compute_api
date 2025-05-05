import React from "react";
import { Card } from "react-bootstrap";
import SectionCard from "./SectionCard.jsx";
import ObjectDisplay from "./ObjectDisplay.jsx";

function PersonRolesDisplay({ personRoles }) {
    if (!personRoles || Object.keys(personRoles).length === 0) {
        return null; // Don't render if no roles
    }

    return (
        <SectionCard title="Person Roles">
            {Object.entries(personRoles).map(([id, roleObj]) => (
                <Card key={id} className="mb-3">
                    <Card.Header as="h6">
                        Person {id}: {roleObj.name || "N/A"}
                    </Card.Header>
                    <Card.Body>
                        {roleObj.role && (
                            <Card.Subtitle className="mb-2 text-gray-500">
                                Role: {roleObj.role}
                            </Card.Subtitle>
                        )}
                        {roleObj.persona && (
                            <Card.Text>
                                <strong>Persona:</strong> {roleObj.persona}
                            </Card.Text>
                        )}
                        {roleObj.voice_config && (
                            <div className="mt-2">
                                <strong>Voice Config:</strong>
                                <ObjectDisplay data={roleObj.voice_config} />
                            </div>
                        )}
                    </Card.Body>
                </Card>
            ))}
        </SectionCard>
    );
}

export default PersonRolesDisplay;
