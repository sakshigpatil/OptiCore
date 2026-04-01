import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from './Header';
import Sidebar from './Sidebar';
import Chatbot from '../common/Chatbot';
import './Layout.css';

const Layout = () => {
  return (
    <div className="layout">
      <Header />
      <div className="layout-body">
        <Sidebar />
        <main className="main-content">
          <Outlet />
        </main>
      </div>
      <Chatbot />
    </div>
  );
};

export default Layout;