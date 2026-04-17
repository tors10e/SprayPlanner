import React, { useState } from 'react';
import Button from 'react-bootstrap/Button';
import Modal from 'react-bootstrap/Modal';
import Image from 'react-bootstrap/Image';
import Card from 'react-bootstrap/Card';


function Bsmodal(props) {
  const [show, setShow] = useState(false);

  const handleClose = () => setShow(false);
  const handleShow = () => setShow(true);

  return (
    <div class="col-sm plus-block--item" >
        <div class="plus-block--item-wrapper inline">
    <>
     <Card style={{ width: '18rem' }}>
      <Card.Img variant="top" src={props.image_src} />
      <Card.Body>
        <Card.Title>{props.title_text}</Card.Title>
        <Card.Text>
        </Card.Text>
        <Button variant="primary" onClick={handleShow}>Learn more</Button>
      </Card.Body>
    </Card>
      <Modal show={show} onHide={handleClose}>
        <Modal.Header closeButton>
          <Modal.Title>{props.title_text}</Modal.Title>
        </Modal.Header>
        <Modal.Body>{props.body_text}</Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleClose}>
            Close
          </Button>
        </Modal.Footer>
      </Modal>
    </>
    </div>
    </div>

);
};

export default Bsmodal;