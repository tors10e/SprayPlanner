import React from 'react';
import banner_image from "../images/banners/pavilion_rock_art_2000.jpg";
import { Container, Col, Row, Image, Card } from 'react-bootstrap';

export function Wedding_Banner(props) {
    return (
        <Container id="wedding_banner">
            <div class="pb-2">
                <img src={banner_image} alt="Sunset View" className="border border-light rounded"/>
            </div>
        </Container>
    )
}

export default Wedding_Banner;