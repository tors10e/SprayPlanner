import React from 'react';
import { Container, Image } from 'react-bootstrap';
import banner_image from "../images/banners/tasting_room_2000x1000.jpg";


export function Banner(props) {
    return (
        <Container id="banner">
            <Image src={banner_image} fluid className="bg-image d-flex justify-content-center align-items-center" />
        </Container>
    )
}

export default Banner;