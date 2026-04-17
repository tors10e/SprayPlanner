import React from 'react';
import {TerraCard} from '../components/terra_card';
import TextDirections from './text_directions';


export function Directions() {
    return(
    <>
     <div class="topic section-heading">
                <h2 id="directions">Directions</h2>
                <div class="container">
                    <div class="row">
                        <ClarkesvilleDirections />
                        <ClaytonDirections />
                        <HelenDirections />
                        <TallulahDirections />
                    </div>
                </div>
     </div>
    </>
    );
};

export function ClarkesvilleDirections(props) {

    const directions = [
                        "Follow Historic 441 for 2 mi.",
                        "Turn left on New Liberty Rd. for 7 mi.",
                        "Turn right on Low Gap Rd. for 3.6 mi.",
                        "Turn right on Vandiver Mtn. Rd. for 1.2 mi"
];

    return(
            <TerraCard
                card_title="From Clarkesville (13 mi)"
                card_text= <TextDirections text_directions={directions} />
                button_text="Chart on Google Maps"
                button_href="https://www.google.com/maps/dir/Clayton,+Georgia+30525/Vandiver+Mountain+Rd,+Georgia/@34.807062,-83.5383547,12z/am=t/data=!4m13!4m12!1m5!1m1!1s0x8858dabf68ad91b7:0xc7f40afdec4f498d!2m2!1d-83.4009933!2d34.8781479!1m5!1m1!1s0x8858c982f82186f5:0xaa8cd4c722afaf3f!2m2!1d-83.4992099!2d34.731045"
            />
    );
};


export function ClaytonDirections(props) {

    const directions = [
                        "Follow US-76 West for 16.9 mi.",
                        "Turn left on Charlie Mountain Rd. for 3.6 mi.",
                        "Turn right on Bridge Creek Rd. for 2 mi.",
                        "Turn left on Seed Lake Rd. for 4.4 mi.",
                        "Turn right on Low Gap Rd. 4.2 mi.",
                        "Turn left on Vandiver Mtn. Rd. for 1.2 mi"
];

    return(
            <TerraCard
                card_title="From Clayton (19 mi)"
                card_text= <TextDirections text_directions={directions} />
                button_text="Chart on Google Maps"
                button_href="https://www.google.com/maps/dir/Clayton,+Georgia+30525/Vandiver+Mountain+Rd,+Georgia/@34.807062,-83.5383547,12z/am=t/data=!4m13!4m12!1m5!1m1!1s0x8858dabf68ad91b7:0xc7f40afdec4f498d!2m2!1d-83.4009933!2d34.8781479!1m5!1m1!1s0x8858c982f82186f5:0xaa8cd4c722afaf3f!2m2!1d-83.4992099!2d34.731045"
            />
    );
};


export function HelenDirections(props) {

    const directions = [
                        "Follow GA-17 East for 2.2 mi.",
                        "Turn left on to GA-255 at Sautee for 7.7 mi.",
                        "Turn right on to GA-197 for 2.3 mi.",
                        "Turn left on to Watts Mill Rd. for 1.2 mi.",
                        "Turn right on Oakey Mtn. Rd. for 4.3 mi.",
                        "Turn left on Low Gap Rd. 4.2 mi.",
                        "Turn left on Vandiver Mtn. Rd. for 1.2 mi"
];

    return(
            <TerraCard
                card_title="From Helen, Cleveland, Sautee (22 mi)"
                card_text= <TextDirections text_directions={directions} />
                button_text="Chart on Google Maps"
                button_href="https://www.google.com/maps/dir/34.6848302,-83.709846/Terra+Incognita+Vineyard,+Vandiver+Mountain+Road,+Clarkesville,+GA/@34.7164852,-83.6417451,12.75z/data=!4m19!4m18!1m10!3m4!1m2!1d-83.6743233!2d34.683858!3s0x885f4a1dba398ca1:0x95b80e1fb8a54480!3m4!1m2!1d-83.5240395!2d34.708332!3s0x8858ca144d8be38b:0xbe605d406e621734!1m5!1m1!1s0x8858c915d77b42fd:0x4c7a8c1b7677a54d!2m2!1d-83.4976891!2d34.7295813!3e0"
            />
    );
};


export function TallulahDirections(props) {

    const directions = [
                        "Follow 441N for 1.2 mi.",
                        "Turn left on to Old 441 for 2.6 mi.",
                        "Turn left on to Lake Rabun Rd. for 6.3 mi.",
                        "Turn left on Low Gap Rd. 4.2 mi.",
                        "Turn left on Vandiver Mtn. Rd. for 1.2 mi"
];

    return(
            <TerraCard
                card_title="From Tallulah Gorge (15 mi)"
                card_text= <TextDirections text_directions={directions} />
                button_text="Chart on Google Maps"
                button_href="https://www.google.com/maps/dir/Tallulah+Gorge+State+Park,+338+Jane+Hurt+Yarn+Rd,+Tallulah+Falls,+GA+30573/Terra+Incognita+Vineyard,+Vandiver+Mountain+Road,+Clarkesville,+GA/@34.7545624,-83.4935558,13z/am=t/data=!3m1!4b1!4m19!4m18!1m10!1m1!1s0x8858c6fec0b2e6a1:0x121373585bc0f494!2m2!1d-83.3964755!2d34.7427244!3m4!1m2!1d-83.3986342!2d34.7646381!3s0x8858c67316d99ce3:0x6eede083255604b7!1m5!1m1!1s0x8858c915d77b42fd:0x4c7a8c1b7677a54d!2m2!1d83.4976891!2d34.7295813!3e0"
            />
    );
};