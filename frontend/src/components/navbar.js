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
              <Nav.Link href="/spray-products">Spray Products</Nav.Link>
              <Nav.Link href="/history">Spray History</Nav.Link>
              <Nav.Link href="/planner">Spray Planner</Nav.Link>
              <Nav.Link href="/reports">Reports</Nav.Link>
              <Nav.Link href="/vineyard-blocks">Vineyard Blocks</Nav.Link>
              <Nav.Link href="/admin">Admin</Nav.Link>
              <Nav.Link href="https://www.wunderground.com/dashboard/pws/KGALAKEM20" target="_blank">Current Weather</Nav.Link>            </Nav>
        </Navbar.Collapse>
      </Navbar>
    </Container>
  );
}

export default TerraNavbar;
