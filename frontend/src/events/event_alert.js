import React from 'react';
import Alert from 'react-bootstrap/Alert';
import ListGroup from 'react-bootstrap/ListGroup';
import {events,} from './list_of_events';
import {GetDayOfTheWeek, StringToDayOfTheWeek, MakeDateNiceToRead} from '../components/utilities';
import Card from 'react-bootstrap/Card';


export function Href(props){
    return <a href={props.link} target="_blank">{props.text}</a>
};


function EventAlert(props) {
  return    <>
            <Card style={{ width: '30rem' }} border="secondary" bg="light">
              <Card.Img variant="top" src={props.image} />
              <Card.Body>
                <Card.Title>{props.title}</Card.Title>
                <Card.Text>{props.description}</Card.Text>
              </Card.Body>
            </Card>
            </>
 }

 


export function EventAlerts() {
    const current_events = CurrentEvents();
    const eventAlerts = current_events.map((event) =>
        <EventAlert key={event[0]} title = {event[0]} description = {event[1]} image={event[2]} />
            );
    return (
        <div>{eventAlerts}</div>
    );
}


// Get raw events from event list file.
function GetEvents() {
    if (typeof events !==  'undefined') //if there is a list just send it.
        {return events}
    else
        {var no_events = [] //if theres not a list, make a blank array and send it.
            return no_events;
         }
}


function IsEventCurrent(event_date, current_date) {
    var isCurrent = false;
    if (event_date >= current_date) {
       isCurrent = true;
    }
    return isCurrent;
 }


export function CurrentEvents(props) {
    var current_events = [];
    // Set current date without time part so that a comparison by day is possible without having to deal with time.
    const current_date = new Date(new Date().toDateString());
    var event_list = GetEvents();
    event_list.map((event) => {
        const event_date = new Date(event[0])
        if (IsEventCurrent(event_date, current_date) == true) {
            var pretty_date = MakeDateNiceToRead(event_date)
            const new_event = [pretty_date, event[1], event[2]];
            current_events.push(new_event);
        }
    })
    // if there are no current events, add an entry to tell people
    if (current_events.length < 1)
        {
            current_events.push([MakeDateNiceToRead(new Date()), 'No current events']);
        }

    return (current_events)
}