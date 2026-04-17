import React from 'react';
import NavBar from "../components/navbar";
import {EventAlerts} from '../events/event_alert';
import ReactGA from "react-ga4";
import { Container, Row } from 'react-bootstrap';

const Events = () => {
    ReactGA.send({ hitType: "pageview", page: "/events", title: "Events" });
    return (
        <Container>
            <Row>
                <NavBar/>
            </Row>
            <Row>
                <EventAlerts/>
            </Row>
        </Container>
    );
};

export default Events;