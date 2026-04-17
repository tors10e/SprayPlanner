import React from "react";
import {PrimaryAlert, SecondaryAlert}  from '../components/alerts';
import {StringToDayOfTheWeek} from '../components/utilities';
import {CurrentEvents} from '../events/event_alert';

// This pulls the first event from list_of_events and displays it on the homepage to get attention.
//todo: make it so that we pull the closest event in the future instead of the first event.

function HomeAlerts() {
    const current_events = CurrentEvents();
    var event_date = new Date(current_events[0][0])

    if (current_events.length > 0 && event_date !=  "Invalid Date") {
        return (
            <>   
                <PrimaryAlert text={<a href="/events">{current_events[0][0]} - {current_events[0][1]}</a>}/>
            </>
        );
    }
};

export default HomeAlerts;