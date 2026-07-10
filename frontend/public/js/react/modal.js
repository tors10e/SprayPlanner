'use strict';

function CabernetModal(props) {
    return React.createElement(Modal, {
        id: "cabernet-modal",
        jquery_id: "#cabernet-modal",
        image_source: "./images/1000x1000/cab_sav_1000x1000.jpg",
        name: "Cabernet Sauvignon",
        modal_text: "Notes of plum, black cherry and tobacco meld to create a medium body and lightly oaked red wine\r that's perfect for settling into a relaxing evening."
    });
}

function Modal(props) {
    return React.createElement(
        "div",
        { "class": "plus-block--item-wrapper inline", onClick: ShowModal },
        React.createElement(
            "div",
            { "class": "plus-block--img-wrapper" },
            React.createElement("img", { src: props.image_source }),
            React.createElement(
                "h3",
                null,
                props.name
            ),
            React.createElement(
                "div",
                { "class": "modal fade", id: props.id, tabindex: "-1", role: "dialog", "aria-hidden": "true" },
                React.createElement(
                    "div",
                    { "class": "modal-dialog", role: "document" },
                    React.createElement(
                        "div",
                        { "class": "modal-content" },
                        React.createElement(ModalHeader, { name: props.name }),
                        React.createElement(ModalBody, { text: props.modal_text })
                    )
                )
            )
        )
    );
}

function ModalHeader(props) {
    return React.createElement(
        "div",
        { "class": "modal-header" },
        React.createElement(
            "h5",
            { "class": "modal-title" },
            props.name
        ),
        React.createElement(
            "button",
            { type: "button", "class": "close", onClick: HideModal, "aria-label": "Close" },
            React.createElement(
                "span",
                { "aria-hidden": "true" },
                "\xD7"
            )
        )
    );
}

function ModalBody(props) {
    return React.createElement(
        "div",
        { "class": "modal-body" },
        React.createElement(
            "p",
            null,
            props.text
        )
    );
}

function ShowModal(props) {
    return $("#cabernet-modal").modal('show');
}

function HideModal(props) {
    return $('#cabernet-modal').modal('hide');
}

var domContainer = document.querySelector('#modal_container');
ReactDOM.render(React.createElement(CabernetModal, null), domContainer);