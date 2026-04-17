import React from 'react';
import ReactGA from "react-ga4";

import Container from 'react-bootstrap/Container';
import Row from 'react-bootstrap/Row';
import Col from 'react-bootstrap/Col';

import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';
import {TerraCard} from '../components/card';
import Gift_Card_Image from "../images/products/square_gift_card.jpg";


const Home = () => {
   ReactGA.send({ hitType: "pageview", page: window.location.pathname, title: "Store" });
    return (
            <>
                <Container>
                    <Row>
                    <Col></Col>
                        <Col>
                            <TerraCard
                                card_title="E-Gift Card"
                                card_text="Purchase an e-gift card to Terra to give a special adventure to
                                    friends and family."
                                card_image={Gift_Card_Image}
                                button_href="https://squareup.com/gift/K1DW0910BX83D/order"
                                button_text="Buy Now">
                            </TerraCard>
                        </Col>
                        <Col></Col>
                    </Row>
                </Container>
            </>
            );
};

export default Home;
