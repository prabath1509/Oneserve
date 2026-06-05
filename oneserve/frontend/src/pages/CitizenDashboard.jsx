import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { FileText, CheckCircle, Clock, Award, TrendingUp } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import { PieChartComponent, BarChartComponent, LineChartComponent } from '../components/Charts';
import api from '../api/axios';
import toast from 'react-hot-toast';

const CitizenDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/citizen');
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

  // Transform data for charts
  const categoryData = Object.entries(stats?.complaints_by_category || {}).map(([name, value]) => ({
    name,
    value,
  }));

  const statusData = Object.entries(stats?.complaints_by_status || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-6 lg:p-8">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600 mt-1">Welcome to your OneServe portal</p>
          </div>

          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6 mb-8">
            <StatCard
              title="Total Complaints"
              value={stats?.total_complaints || 0}
              icon={FileText}
              color="primary"
            />
            <StatCard
              title="Pending"
              value={stats?.pending_complaints || 0}
              icon={Clock}
              color="warning"
            />
            <StatCard
              title="Resolved"
              value={stats?.resolved_complaints || 0}
              icon={CheckCircle}
              color="success"
            />
            <StatCard
              title="Applications"
              value={stats?.total_applications || 0}
              icon={Award}
              color="purple"
            />
            <StatCard
              title="Approved Certificates"
              value={stats?.approved_certificates || 0}
              icon={TrendingUp}
              color="success"
            />
          </div>

          {/* Quick Actions */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <button
              onClick={() => navigate('/complaints/create')}
              className="card hover:shadow-lg transition-shadow text-left"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-primary-100 rounded-lg">
                  <FileText className="h-6 w-6 text-primary-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">File Complaint</h3>
                  <p className="text-sm text-gray-600">Report a new issue</p>
                </div>
              </div>
            </button>

            <button
              onClick={() => navigate('/locker/upload')}
              className="card hover:shadow-lg transition-shadow text-left"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-success-100 rounded-lg">
                  <FileText className="h-6 w-6 text-success-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Upload Document</h3>
                  <p className="text-sm text-gray-600">Add to DigiLocker</p>
                </div>
              </div>
            </button>

            <button
              onClick={() => navigate('/certificates/apply')}
              className="card hover:shadow-lg transition-shadow text-left"
            >
              <div className="flex items-center space-x-4">
                <div className="p-3 bg-purple-100 rounded-lg">
                  <Award className="h-6 w-6 text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-gray-900">Apply Certificate</h3>
                  <p className="text-sm text-gray-600">Request new certificate</p>
                </div>
              </div>
            </button>
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {categoryData.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Complaints by Category
                </h3>
                <PieChartComponent data={categoryData} />
              </div>
            )}

            {statusData.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Complaints by Status
                </h3>
                <BarChartComponent data={statusData} xAxisKey="name" dataKey="value" />
              </div>
            )}

            {stats?.monthly_complaints && stats.monthly_complaints.length > 0 && (
              <div className="card lg:col-span-2">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Monthly Complaint Trend
                </h3>
                <LineChartComponent 
                  data={stats.monthly_complaints} 
                  xAxisKey="month" 
                  dataKey="count" 
                />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default CitizenDashboard;
