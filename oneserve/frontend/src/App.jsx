import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Toaster } from 'react-hot-toast';
import ProtectedRoute from './components/ProtectedRoute';

// Auth pages
import Login from './pages/Login';
import Register from './pages/Register';

// Citizen pages
import CitizenDashboard from './pages/CitizenDashboard';
import ComplaintCreate from './pages/Complaints/ComplaintCreate';
import ComplaintList from './pages/Complaints/ComplaintList';
import ComplaintDetails from './pages/Complaints/ComplaintDetails';
import LockerUpload from './pages/Locker/LockerUpload';
import LockerList from './pages/Locker/LockerList';
import CertificateApply from './pages/Certificates/CertificateApply';
import CertificateList from './pages/Certificates/CertificateList';
import CertificateDetails from './pages/Certificates/CertificateDetails';

// Officer pages
import OfficerDashboard from './pages/OfficerDashboard';

// Admin pages
import AdminDashboard from './pages/AdminDashboard';
import CertificateAdminReview from './pages/Certificates/CertificateAdminReview';
import AdminCertificateReview from './pages/Admin/AdminCertificateReview';
import ManageUsers from './pages/Admin/ManageUsers';

// Shared pages
import Notifications from './pages/Notifications';

const AppRoutes = () => {
  const { user } = useAuth();

  const getDashboardPath = () => {
    if (!user) return '/login';
    if (user.role === 'CITIZEN') return '/dashboard';
    if (user.role?.startsWith('OFFICER_')) return '/officer/dashboard';
    if (user.role === 'ADMIN') return '/admin/dashboard';
    return '/login';
  };

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={getDashboardPath()} /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to={getDashboardPath()} /> : <Register />} />
      
      {/* Citizen routes */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <CitizenDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <ComplaintList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints/create"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <ComplaintCreate />
          </ProtectedRoute>
        }
      />
      <Route
        path="/complaints/:id"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN', 'OFFICER_WATER', 'OFFICER_ELECTRICITY', 'OFFICER_ROAD', 'OFFICER_SANITATION', 'ADMIN']}>
            <ComplaintDetails />
          </ProtectedRoute>
        }
      />
      <Route
        path="/locker"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <LockerList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/locker/upload"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <LockerUpload />
          </ProtectedRoute>
        }
      />
      <Route
        path="/certificates"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <CertificateList />
          </ProtectedRoute>
        }
      />
      <Route
        path="/certificates/apply"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN']}>
            <CertificateApply />
          </ProtectedRoute>
        }
      />
      <Route
        path="/certificates/:id"
        element={
          <ProtectedRoute allowedRoles={['CITIZEN', 'ADMIN']}>
            <CertificateDetails />
          </ProtectedRoute>
        }
      />
      
      {/* Officer routes */}
      <Route
        path="/officer/dashboard"
        element={
          <ProtectedRoute allowedRoles={['OFFICER_WATER', 'OFFICER_ELECTRICITY', 'OFFICER_ROAD', 'OFFICER_SANITATION']}>
            <OfficerDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/officer/complaints"
        element={
          <ProtectedRoute allowedRoles={['OFFICER_WATER', 'OFFICER_ELECTRICITY', 'OFFICER_ROAD', 'OFFICER_SANITATION']}>
            <ComplaintList />
          </ProtectedRoute>
        }
      />
      
      {/* Admin routes */}
      <Route
        path="/admin/dashboard"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminDashboard />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/certificates"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <CertificateAdminReview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/certificates/:id"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <AdminCertificateReview />
          </ProtectedRoute>
        }
      />
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute allowedRoles={['ADMIN']}>
            <ManageUsers />
          </ProtectedRoute>
        }
      />
      
      {/* Shared routes */}
      <Route
        path="/notifications"
        element={
          <ProtectedRoute>
            <Notifications />
          </ProtectedRoute>
        }
      />
      
      <Route path="/" element={<Navigate to={getDashboardPath()} />} />
      <Route path="*" element={<Navigate to={getDashboardPath()} />} />
    </Routes>
  );
};

function App() {
  return (
    <AuthProvider>
      <Router>
        <Toaster position="top-right" />
        <AppRoutes />
      </Router>
    </AuthProvider>
  );
}

export default App;
