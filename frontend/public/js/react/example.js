function Welcome(props) {
  return React.createElement(
    "h1",
    null,
    "Hello, ",
    props.name
  );
}

var element = React.createElement(Welcome, { name: "Sara" });
ReactDOM.render(element, document.getElementById('root'));