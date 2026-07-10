import Button from 'react-bootstrap/Button';
import Card from 'react-bootstrap/Card';

{/* Default card with terra look and feel */}
 function TerraCard(props) {
  return (
    <Card style={{width: '36rem'}}>
      <Card.Body>
        <Card.Img variant="top" src={props.card_image} />
        <Card.Title>{props.card_title}</Card.Title>
        <Card.Text>{props.card_text}</Card.Text>
        <Button variant={props.button_variant} href={props.button_href}>{props.button_text}</Button>
      </Card.Body>
    </Card>
  );
}

{/* This card is used for overlaying text on an image */}
 function OverlayCard(props) {
  return (
    <Card style={{width: '100%'}} className="bg-dark text-white">
      <Card.Img src={props.card_image} alt="Card image" />
      <Card.ImgOverlay>
        <Card.Title>{props.card_title}</Card.Title>
        <Card.Text>{props.card_text}</Card.Text>
        <Card.Text>{props.additional_text}</Card.Text>
      </Card.ImgOverlay>
    </Card>
  );
}


{/*This overlay card is clickable*/}
function ClickableOverlayCard(props) {
  return(
    <a href={props.url}>
      <OverlayCard card_title={props.card_title} card_text={props.card_text} card_image={props.card_image}/>
    </a>
  )
}


export {TerraCard, OverlayCard, ClickableOverlayCard};