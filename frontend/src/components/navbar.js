import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';
import NavDropdown from 'react-bootstrap/NavDropdown';


function TerraNavbar(props) {
  return (
    <Container>
      <Navbar  bg="white" expand="lg" >
       {/* <Navbar.Brand href="/#home">Terra Incognita</Navbar.Brand> */}
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="m-auto">
            <Nav.Link href="/">Home</Nav.Link>
            <Nav.Link href="/#footer">Hours</Nav.Link>
            <Nav.Link href="https://www.wunderground.com/dashboard/pws/KGALAKEM20" target="_blank">Current Weather</Nav.Link>
            <Nav.Link href="https://www.google.com/maps/dir//Terra+Incognita+Vineyard,+1821+Vandiver+Mountain+Rd,+Clarkesville,+GA+30523/@34.7333066,-83.5026561,17z/data=!4m9!4m8!1m0!1m5!1m1!1s0x8858c915d77b42fd:0x4c7a8c1b7677a54d!2m2!1d-83.5026561!2d34.7333066!3e0?entry=ttu&g_ep=EgoyMDI1MDExNS4wIKXMDSoASAFQAw%3D%3D" 
                target="_blank">
                Directions</Nav.Link>
            <Nav.Link href="/events">Events</Nav.Link>
            <NavDropdown title="Weddings" id="basic-nav-dropdown">
              <NavDropdown.Item href="/weddings">Wedding Information</NavDropdown.Item>
              <NavDropdown.Item href="/wedding-pricing"> Wedding Pricing</NavDropdown.Item>
            </NavDropdown>
            <Nav.Link href="/gallery">Gallery</Nav.Link>
            <Nav.Link href="/overnighting">Overnighting</Nav.Link>
            <Nav.Link href="/trails">Trails</Nav.Link>
            <Nav.Link href="/store">Store</Nav.Link>
            <Nav.Link href="/database">Database</Nav.Link>
            <Nav.Link href="/#footer">Contact</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Navbar>
    </Container>
    );
  }


export default TerraNavbar;