import React from 'react';
import { Container, Col, Row, Image, Card } from 'react-bootstrap';

export function Wedding_Banner(props) {
    return (
        <Container id="wedding_banner">
            <div className="text-white text-center py-4" style={{ backgroundColor: "#002855", width: "100%" }}>
                <h1 className="m-0">Wedding Pricing</h1>
            </div>
        </Container>
    )
}

export default Wedding_Banner;