import React from 'react';
import {Col, Row, Image} from 'react-bootstrap';

import logo from "../images/logo_bw_text.png";

function Header(props) {
    return (
        <Row>
            <Col class="col-4"></Col>
            <Col class="col-2" >
                <div class="pb-2 pt-4">
                    <Image src={logo} width="200px"/>
                </div>
            </Col>
            <Col class="col-4"></Col>
        </Row>
    );
}

export default Header;