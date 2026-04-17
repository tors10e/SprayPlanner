import React from 'react';
import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';
import Image from 'react-bootstrap/Image';

import {TerraCard} from '../components/card';
import camping_summer from '../images/camping_summer.jpg';
import alpenglow_apartment_interior from '../images/alpenglow_apartment_interior.jpg';
import NorthernViewFromWRidge from '../images/NorthernViewFromWRidge.png';
import {PrimaryAlert, SecondaryAlert}  from '../components/alerts';
import ReactGA from 'react-ga4';

function Alerts() {
    ReactGA.send({ hitType: "pageview", page: "/overnighting", title: "Overnighting" });
   return(
        <PrimaryAlert text='Apartment rental is back! Unfortunately, Rabun County no longer allows camping on agricultural lands, sorry for the
        inconvenience.'/>
    )
};


function Intro() {
return(
        <div className="topic topic-even section-heading">
            <Container>
                <Row>
                    <Col>
                        <TerraCard card_image={camping_summer} card_title='Camping - (Closed until county regulations are navigated)'
                            card_text='Best of 2022 Finalist at HipCamp! Our campsite is available on the West Ridge with
                                spectacular views of the Southern Nantahala Wilderness, including peaks pushing ,5500 feet!
                                We now have a 12 x 20 ft pavilion thats perfect for getting out of the rain or setting
                                up hammocks. Since we limit camping to one group, you will have the place to yourself,
                                great for groups with multiple tents, roof-top tents, or single tents.'
                            button_text='Book Camping Here'
                            button_variant='primary'
                            button_href='https://www.hipcamp.com/en-US/georgia/torsten-e-s-land/terra-incognita-vineyard'
                        />
                    </Col>
                    <Col>
                        <TerraCard card_image={alpenglow_apartment_interior}
                            card_title='Apartment Rental'
                            card_text='Come spend the night in the Alpenglow Suite and have the Tallulah Mountains to yourselves!
                                Our studio apartment on the East Ridge, provides lodging for 2 people plus a pullout couch
                                for additional guests. The interior is furnished with oak that was harvested from our official
                                Forest Stewardardship Program (FSP) woodlands. Spectacular views of the mountains of North
                                Carolina and Rabun Bald. Completely surrounded by thousands of acres of National Forest,
                                the Alpenglow is perfect for those seeking solitude.  To book directly  email or call us.'
                            button_text='Book the Alpenglow Suite Here'
                            button_href='https://www.vrbo.com/2328117?adultsCount=2&unitId=2894423'
                        />
                    </Col>
                </Row>
            </Container>
        </div>
    )
};


function Overnighting() {
    return (
    <div className="d-flex w-100 h-100 mx-auto flex-column">
                <Alerts />
                <div className="container">
                    <Intro />
                </div>
        </div>
    )
}


export default Overnighting;