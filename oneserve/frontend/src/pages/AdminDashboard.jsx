import { useState, useEffect } from 'react';
import { Users, FileText, Award, Folder, TrendingUp } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import { LineChartComponent } from '../components/Charts';
import api from '../api/axios';
import toast from 'react-hot-toast';

const AdminDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/admin');
      setStats(response.data);
    } catch (error) {
      toast.error('Error loading dashboard');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-6 lg:p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Admin Dashboard</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-6 mb-8">
            <StatCard
              title="Total Users"
              value={stats?.total_users || 0}
              icon={Users}
              color="primary"
            />
            <StatCard
              title="Citizens"
              value={stats?.total_citizens || 0}
              icon={Users}
              color="success"
            />
            <StatCard
              title="Officers"
              value={stats?.total_officers || 0}
              icon={Users}
              color="purple"
            />
            <StatCard
              title="Pending Applications"
              value={stats?.pending_certificate_applications || 0}
              icon={Award}
              color="warning"
            />
            <StatCard
              title="Pending Complaints"
              value={stats?.pending_complaints || 0}
              icon={FileText}
              color="danger"
            />
            <StatCard
              title="Documents"
              value={stats?.documents_uploaded || 0}
              icon={Folder}
              color="primary"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
            {stats?.applications_trend && stats.applications_trend.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Certificate Applications Trend
                </h3>
                <LineChartComponent 
                  data={stats.applications_trend} 
                  xAxisKey="month" 
                  dataKey="count" 
                />
              </div>
            )}

            {stats?.complaint_performance && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Complaint Resolution Performance
                </h3>
                <div className="space-y-4">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Total Complaints:</span>
                    <span className="font-semibold">{stats.complaint_performance.total}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Resolved:</span>
                    <span className="font-semibold text-success-600">{stats.complaint_performance.resolved}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">In Progress:</span>
                    <span className="font-semibold text-primary-600">{stats.complaint_performance.in_progress}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-600">Pending:</span>
                    <span className="font-semibold text-warning-600">{stats.complaint_performance.pending}</span>
                  </div>
                  <div className="pt-4 border-t">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Resolution Rate:</span>
                      <span className="font-bold text-xl text-primary-600">{stats.complaint_performance.resolution_rate}%</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;
