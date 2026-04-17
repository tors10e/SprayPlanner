<script type="module" src="href.js"></script>

function Href(props){
    return <a href={props.href} target="_blank">{props.text}</a>
};

export { Href }