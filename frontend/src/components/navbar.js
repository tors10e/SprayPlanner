import Container from 'react-bootstrap/Container';
import Nav from 'react-bootstrap/Nav';
import Navbar from 'react-bootstrap/Navbar';

function TerraNavbar(props) {
  return (
    <Container>
      <Navbar bg="white" expand="lg">
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="m-auto">
            <Nav.Link href="/database">Database</Nav.Link>
            <Nav.Link href="https://www.wunderground.com/dashboard/pws/KGALAKEM20" target="_blank">Current Weather</Nav.Link>
          </Nav>
        </Navbar.Collapse>
      </Navbar>
    </Container>
  );
}

export default TerraNavbar;
