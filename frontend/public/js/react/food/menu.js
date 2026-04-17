
function Menu(props) {
    return React.createElement(
        "div",
        null,
        React.createElement(
            "h2",
            { "class": "text-decoration-underline heading" },
            "Terra's Food Menu"
        ),
        React.createElement(
            "table",
            { "class": "table table-striped" },
            React.createElement(
                "tbody",
                null,
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Hummus and Pita Chips"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Organic lemon and garlic hummus served with pita chips."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Stuffed Grape Leaves"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "A blend of white rice, onion, and mint, wrapped in tender grape leaves."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Charcuterie Plate"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Cured prosciutto and salami with gorgonzola, cranberry wensleydale, and sage derby cheese, green olives, roasted almonds, dried apricots, and pita chips."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Flatbread Pizza"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Naan flatbread with your choice of pesto or marinara sauce, mozzarella and provolone cheese, topped with arugula and a drizzle of balsamic glaze."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Lobster Bisque"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Shredded lobster blended with clam broth and sherry wine. Served with crusty french bread. *contains milk, shellfish, and wheat."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Tiramisu"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Made from imported mascarpone and sponge cake, soaked in espresso and topped with cocoa."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Stawberry Swirl Cheesecake"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Classic New York style cheesecake with a graham cracker crust and a strawberry swirl."
                    )
                ),
                React.createElement(
                    "tr",
                    null,
                    React.createElement(
                        "th",
                        { scope: "row" },
                        "Limoncello Mascarpone"
                    ),
                    React.createElement(
                        "td",
                        null,
                        "Lemon and limoncello liquor baked into sponge cake with mascarpone icing."
                    )
                )
            )
        )
    );
}

ReactDOM.render(React.createElement(Menu, null), document.getElementById('menu_container'));