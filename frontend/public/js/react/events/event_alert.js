
function Href(props) {
  return React.createElement(
    "a",
    { href: props.link, target: "_blank" },
    props.text
  );
};

function EventAlertEven(props) {
  return React.createElement(
    "div",
    { "class": "topic" },
    React.createElement(
      "div",
      { "class": "alert alert-primary", role: "alert" },
      React.createElement(
        "h2",
        { "class": "cover-heading" },
        props.title
      )
    ),
    React.createElement(
      "p",
      { "class": "lead" },
      props.description
    )
  );
}

function EventAlertOdd(props) {
  return React.createElement(
    "div",
    { "class": "topic" },
    React.createElement(
      "div",
      { "class": "alert alert-secondary", role: "alert" },
      React.createElement(
        "h2",
        { "class": "cover-heading" },
        props.title
      )
    ),
    React.createElement(
      "p",
      { "class": "lead" },
      props.description
    )
  );
}

function EventAlerts() {
  var eventAlerts = events.map(function (event) {
    return React.createElement(EventAlertOdd, { title: event[0], description: event[1] });
  });

  return React.createElement(
    "div",
    null,
    eventAlerts
  );
}

function makeHref(httpLink, linkText) {
  return React.createElement(Href, { link: httpLink, text: linkText });
}

var events = [["Saturday July 30th, 2022 - Live Music by George James", "George will be playing starting at 2 pm so come early to enjoy his music."], ["Saturday August 6th, 2022 - Live Music by High Lonesome", "Philmer and Lisa Kilby will be entertaining us with their phenomenal guitar and vocals!"], ["Saturday August 13th, 2022 - Live Music by Scott Low", ""], ["Saturday August 20th, 2022 - Live Music by Jake Hicks", "Another one of our regular performers, happy to have him back!"], ["Sunday August 21st - Wildcraft Kitchen Mushroom Foray", makeHref("https://www.wildcraftkitchenga.com/", "Wildcraft Kitchen's website!")]];

ReactDOM.render(React.createElement(EventAlerts, { titles: events }), document.getElementById('event_alert_container'));