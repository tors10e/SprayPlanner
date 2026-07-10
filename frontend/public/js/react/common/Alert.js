function PrimaryAlert(props) {
    return React.createElement(
        "div",
        { "class": "alert alert-primary", role: "alert" },
        React.createElement(
            "div",
            { "class": "cover-heading" },
            props.text
        ),
        React.createElement("img", { src: props.image_url, "class": "rounded",
            alt: props.image_alt })
    );
}

function DangerAlert(props) {
    return React.createElement(
        "div",
        { "class": "alert alert-danger", role: "alert" },
        React.createElement(
            "div",
            { "class": "cover-heading" },
            props.text
        )
    );
}

export default PrimaryAlert;