import React from 'react';


//This takes a list of text directions and creates an ordered list from them.
function TextDirections(props) {
    const directionList = props.text_directions.map((direction) =>
        <li>{direction}</li>
        );

    return (
        <ol>{directionList}</ol>
        );
};


export default TextDirections;