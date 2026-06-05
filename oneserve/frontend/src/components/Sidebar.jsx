import { Link, useLocation } from 'react-router-dom';
import { 
  Home, 
  FileText, 
  Folder, 
  Award, 
  Bell, 
  Users,
  X 
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const Sidebar = ({ isOpen, onClose }) => {
  const location = useLocation();
  const { user } = useAuth();

  const citizenLinks = [
    { path: '/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/complaints', icon: FileText, label: 'Complaints' },
    { path: '/locker', icon: Folder, label: 'DigiLocker' },
    { path: '/certificates', icon: Award, label: 'Certificates' },
    { path: '/notifications', icon: Bell, label: 'Notifications' },
  ];

  const officerLinks = [
    { path: '/officer/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/officer/complaints', icon: FileText, label: 'Assigned Complaints' },
    { path: '/notifications', icon: Bell, label: 'Notifications' },
  ];

  const adminLinks = [
    { path: '/admin/dashboard', icon: Home, label: 'Dashboard' },
    { path: '/admin/certificates', icon: Award, label: 'Certificate Review' },
    { path: '/admin/users', icon: Users, label: 'Manage Users' },
    { path: '/notifications', icon: Bell, label: 'Notifications' },
  ];

  let links = [];
  if (user?.role === 'CITIZEN') {
    links = citizenLinks;
  } else if (user?.role?.startsWith('OFFICER_')) {
    links = officerLinks;
  } else if (user?.role === 'ADMIN') {
    links = adminLinks;
  }

  return (
    <>
      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
          onClick={onClose}
        ></div>
      )}

      {/* Sidebar */}
      <aside
        className={`
          fixed top-0 left-0 z-50 h-screen w-64 bg-white shadow-lg transform transition-transform duration-300 ease-in-out flex flex-col
          lg:translate-x-0 lg:static lg:z-auto lg:h-screen
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        {/* Mobile header */}
        <div className="flex items-center justify-between p-4 border-b lg:hidden flex-shrink-0">
          <span className="text-xl font-bold text-primary-600">Menu</span>
          <button onClick={onClose} className="p-2 rounded-md hover:bg-gray-100">
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Navigation - scrollable if needed */}
        <nav className="flex-1 overflow-y-auto py-8 px-4">
          <ul className="space-y-2">
            {links.map((link) => {
              const Icon = link.icon;
              const isActive = location.pathname === link.path;
              
              return (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    onClick={() => onClose()}
                    className={`
                      flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors
                      ${
                        isActive
                          ? 'bg-primary-50 text-primary-700 font-medium'
                          : 'text-gray-700 hover:bg-gray-100'
                      }
                    `}
                  >
                    <Icon className="h-5 w-5" />
                    <span>{link.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>
      </aside>
    </>
  );
};

export default Sidebar;
