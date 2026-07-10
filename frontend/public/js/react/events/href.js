React.createElement("script", { type: "module", src: "href.js" });

function Href(props) {
    return React.createElement(
        "a",
        { href: props.href, target: "_blank" },
        props.text
    );
};

export { Href };