import React from 'react';
import Alert from 'react-bootstrap/Alert';


export function PrimaryAlert(props) {
    return (
        <Alert key="primary" variant="primary">
                <h2>{props.text}</h2>
        </Alert>
        );
}

export function DangerAlert(props) {
    return (
        <Alert key="danger" variant="danger">
            <h2>{props.text}</h2>
        </Alert>
    );
}

export function SecondaryAlert(props) {
    return (
        <Alert key="secondary" variant="secondary">
        <h2>{props.text}</h2>
        </Alert>
    );
}

function AlertContent(props) {
    return (
        <div class="cover-heading">{props.text}
            <img src={props.image_url} class="rounded" alt={props.image_alt}></img>
        </div>);
}
