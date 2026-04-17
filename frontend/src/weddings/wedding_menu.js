import React from 'react';
import { Container, Col, Row, ListGroupItem, Image } from 'react-bootstrap';
import ListGroup from 'react-bootstrap/ListGroup'


import SunKiss from "../images/event_photos/SunKiss.jpg";
import DJLights from "../images/event_photos/DjLights.jpg";
import CeremonyRock from "../images/event_photos/ceremony_rock.jpg";
import BrianEmilyVows from "../images/event_photos/brian_emily_vows_2000px.jpg";
import Badge2021 from '../images/wedding-rule-badge-2021_213x213.png';
import Badge2022 from '../images/wedding-rule-badge-2022 - high resolution.png';

export function WeddingMenu(props) {
    return (
    <div>
        <Container>
            <Row className="grid-item-margin" xs={1} md={3}>
              
            <Col id="centered-grid-content">
                   <ListGroup variant="flush">
                    <ListGroupItem>2024 Best of GA Regional winner Wedding Venues for the GBJ</ListGroupItem>
                    <ListGroupItem>2023 Best of Georgia Regional winner in the Wedding Venues for the GBJ</ListGroupItem>
                    <ListGroupItem>Chosen Wedding Rule's Atlanta's Top 10 Winery Wedding Venues in 2022</ListGroupItem>
                    <ListGroupItem>Chosen Wedding Rule's Atlanta's Top 10 Winery Wedding Venues in 2021</ListGroupItem>
                   </ListGroup>
                </Col>
                <Col>   <a id="myInput" target="_blank" rel="noopener"
                    href="https://www.weddingrule.com/winery-wedding-venues/georgia/atlanta">
                    <Image src={Badge2021}></Image>
                </a>
                </Col>
                <Col><a id="myInput" target="_blank" rel="noopener"
                    href="https://www.weddingrule.com/winery-wedding-venues/georgia/atlanta">
                    <Image src={Badge2022}></Image></a> 
                </Col>

            </Row>
            <Row>
                <Col id="centered-grid-content">
                    Our tranquil 120 acre mountain farm is completely surrounded by thousands of acres of the Chattahoochee National Forest and offers year-round mountain views of the highest peaks of Nantahalla National Forest.
                </Col>
                <Col><Image className='vertical-align' src={CeremonyRock} rounded></Image></Col>
            </Row>
            <Row>
                <Col> <Image  className='vertical-align' src={SunKiss} rounded></Image> </Col>
                <Col id="centered-grid-content">We are a welcoming venue that accommodates ceremonies for traditional and non-traditional weddings with a wide range of budgets that appeal to nearly any couple.</Col>
            </Row>
            <Row>
                <Col id="centered-grid-content">We are here to help make your vision a reality! Our 3,500 ft2 pavilion is a blank canvas that awaits your imagination. We have an extensive list of vendorsthat offer and array of services that you can choose from or bring you own!</Col>
                <Col><Image  className='vertical-align' src={DJLights} rounded></Image> </Col>
            </Row>
            <Row>
                <Col> <Image  className='vertical-align' src={BrianEmilyVows} rounded></Image> </Col>
                <Col id="centered-grid-content">With a limited amount of weddings per year, we eliminate the production line feeling, ensuring an exclusive event and treasured memory for you and your spouse.</Col>   
            </Row>
        </Container>
    </div>
    );
}

export default WeddingMenu;