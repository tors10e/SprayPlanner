
import Banner from "./banner";
import Header from "../components/header";
import NavBar from "../components/navbar";

import ReactGA from "react-ga4";
import { Container, Col, Row, Image, Card } from 'react-bootstrap';



const Winery = () => {
    ReactGA.send({ hitType: "pageview", page: "/home", title: "Home" });
    return (
            <Container>
                <Row>
                    {<Header/>}
                </Row>
                <Row class="navbar">
                    <NavBar />
                </Row>
                <Row>
                    <Banner/>
                </Row>


            </Container>
    );
};

export default Winery;
