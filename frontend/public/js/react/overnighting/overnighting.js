function Camping(props) {
    return React.createElement(
        "div",
        { className: "topic topic-odd section-heading" },
        React.createElement(
            "h2",
            { id: "camping" },
            "Camping"
        ),
        React.createElement(
            "p",
            null,
            "Unimproved camping is available on the western hillside overlooking the vineyard. Since we limit camping to one group, you'll have the place to yourself. To reserve a spot go to ",
            React.createElement(
                "a",
                {
                    href: "https://www.hipcamp.com/en-US/georgia/torsten-e-s-land/terra-incognita-vineyard",
                    target: "_blank" },
                "https://www.hipcamp.com/en-US/georgia/torsten-e-s-land/terra-incognita-vineyard"
            ),
            ". If you're a current camper, check out the ",
            React.createElement(
                "a",
                { href: "./images/terra_orientation.pdf", target: "_blank" },
                "orientation sheet "
            ),
            "for information on what to expect and what to do."
        )
    );
}

function Apartment(props) {
    return React.createElement(
        "div",
        { className: "topic topic-even section-heading" },
        React.createElement(
            "h2",
            { id: "apartment" },
            "Apartment"
        ),
        React.createElement(
            "p",
            null,
            "Above the pavilion is a beautiful apartment available for rental. Please checkout our \\",
            React.createElement(
                "a",
                { href: "https://www.vrbo.com/2328117?adultsCount=2&arrival=2022-07-14&departure=2022-07-16&unitId=2894423", target: "_blank" },
                "VRBO Listing"
            )
        )
    );
}

function Overnighting(props) {
    return React.createElement(
        "div",
        null,
        React.createElement(Camping, null),
        React.createElement(Apartment, null)
    );
}

ReactDOM.render(React.createElement(Overnighting, null), document.getElementById('overnighting_container'));