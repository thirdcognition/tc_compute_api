import React from "react";
import { Modal, Button } from "react-bootstrap";

const ConfirmationDialog = ({ show, onHide, onConfirm, message }) => {
    return (
        <Modal show={show} onHide={onHide} centered>
            <Modal.Header closeButton>
                <Modal.Title>Confirm Action</Modal.Title>
            </Modal.Header>
            <Modal.Body>
                <p>{message}</p>
            </Modal.Body>
            <Modal.Footer>
                <Button variant="secondary" onClick={onHide}>
                    Cancel
                </Button>
                <Button variant="danger" onClick={onConfirm}>
                    Confirm
                </Button>
            </Modal.Footer>
        </Modal>
    );
};

export default ConfirmationDialog;
