import React from "react";
import { Form } from "react-bootstrap";

function CountryComponent({ value, onChange }) {
    const nordicCountries = [
        { code: "SE", name: "Sweden" },
        { code: "NO", name: "Norway" },
        { code: "FI", name: "Finland" },
        { code: "DK", name: "Denmark" },
        { code: "IS", name: "Iceland" }
    ];

    const euCountries = [
        { code: "DE", name: "Germany" },
        { code: "FR", name: "France" },
        { code: "IT", name: "Italy" },
        { code: "ES", name: "Spain" },
        { code: "PL", name: "Poland" }
    ];

    const usCountries = [{ code: "US", name: "United States" }];

    return (
        <Form.Group controlId="country-select">
            <Form.Label className="font-semibold">Country:</Form.Label>
            <Form.Control
                as="select"
                value={value}
                onChange={(e) => onChange(e.target.value)}
                className="border-gray-300 focus:border-blue-500 focus:ring focus:ring-blue-200 focus:ring-opacity-50 mb-2"
            >
                {nordicCountries.map((country) => (
                    <option key={country.code} value={country.code}>
                        {country.name}
                    </option>
                ))}
                {euCountries.map((country) => (
                    <option key={country.code} value={country.code}>
                        {country.name}
                    </option>
                ))}
                {usCountries.map((country) => (
                    <option key={country.code} value={country.code}>
                        {country.name}
                    </option>
                ))}
            </Form.Control>
        </Form.Group>
    );
}

export default CountryComponent;
