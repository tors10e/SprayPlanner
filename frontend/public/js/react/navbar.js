function NavBar(props) {
    return React.createElement(
        "div",
        null,
        React.createElement(
            "nav",
            { "class": "navbar nav-masthead navbar-expand-lg navbar-normal navbar-fixed-top bg-light" },
            React.createElement(
                "a",
                { "class": "navbar-brand alpha", href: "index.html" },
                "Terra Incognita Vineyard"
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html" },
                "Home"
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html#hours" },
                "Hours"
            ),
            React.createElement(
                "div",
                { "class": "nav-item dropdown" },
                React.createElement(
                    "a",
                    { "class": "nav-link dropdown-toggle", href: "#", id: "navbarDropdown", role: "button",
                        "data-bs-toggle": "dropdown", "aria-expanded": "false" },
                    "Events"
                ),
                React.createElement(
                    "div",
                    { "class": "dropdown-menu", "aria-labelledby": "navbarDropdown" },
                    React.createElement(
                        "a",
                        { "class": "dropdown-item", href: "events_public.html" },
                        "Events"
                    ),
                    React.createElement(
                        "a",
                        { "class": "dropdown-item", href: "events_private.html" },
                        "Private Events"
                    ),
                    React.createElement(
                        "a",
                        { "class": "dropdown-item", href: "events_private.html#weddings" },
                        "Weddings"
                    )
                )
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html#directions" },
                "Directions"
            ),
            React.createElement(
                "div",
                { "class": "nav-item dropdown" },
                React.createElement(
                    "a",
                    { "class": "nav-link dropdown-toggle", href: "#", id: "navbarDropdown", role: "button",
                        "data-bs-toggle": "dropdown", "aria-expanded": "false" },
                    "Food"
                ),
                React.createElement(
                    "div",
                    { "class": "dropdown-menu", "aria-labelledby": "navbarDropdown" },
                    React.createElement(
                        "a",
                        { "class": "dropdown-item", href: "food.html" },
                        "Food Menu"
                    )
                )
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html#camping" },
                "Camping"
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html#trails" },
                "Trails"
            ),
            React.createElement(
                "a",
                { "class": "nav-link", href: "index.html#contact" },
                "Contact"
            ),
            React.createElement(
                "div",
                { "class": "nav-right ml-auto" },
                React.createElement(
                    "a",
                    { href: "https://www.facebook.com/TerraIncognitaVineyard", target: "_blank" },
                    " ",
                    React.createElement("i", {
                        "class": "bi bi-facebook icon-blue" })
                )
            )
        )
    );
}

ReactDOM.render(React.createElement(NavBar, null), document.getElementById('nav_container'));