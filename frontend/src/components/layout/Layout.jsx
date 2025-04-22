import Header from "./Header";
import Footer from "./Footer";
import { Outlet } from "react-router-dom";
import Container from "react-bootstrap/Container";

const Layout = () => {
  return (
    <>
      <Header />
      <main>
        <Container className="my-4">
          <Outlet />
        </Container>
      </main>
      <Footer />
    </>
  );
};

export default Layout;
