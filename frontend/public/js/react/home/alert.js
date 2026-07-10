function PrimaryAlert(props) {
    return React.createElement(
        "div",
        { "class": "alert alert-primary", role: "alert" },
        React.createElement(AlertContent, { text: props.text }),
        React.createElement("img", { src: props.image_url, "class": "rounded", alt: props.image_alt })
    );
}

function DangerAlert(props) {
    return React.createElement(
        "div",
        { "class": "alert alert-danger", role: "alert" },
        React.createElement(AlertContent, { text: props.text })
    );
}

function SecondaryAlert(props) {
    return React.createElement(
        "div",
        { "class": "alert alert-secondary", role: "alert" },
        React.createElement(AlertContent, { text: props.text })
    );
}

function AlertContent(props) {
    return React.createElement(
        "div",
        { "class": "cover-heading" },
        props.text,
        React.createElement("img", { src: props.image_url, "class": "rounded", alt: props.image_alt })
    );
}

function Alerts() {
    return React.createElement(
        "div",
        null,
        React.createElement(SecondaryAlert, { text: React.createElement(
                "a",
                { href: "./events_public.html" },
                "See our events page for upcoming events including when private events require us to use the western hillside for tastings."
            ) })
    );
}

ReactDOM.render(React.createElement(Alerts, null), document.getElementById('alert_container'));