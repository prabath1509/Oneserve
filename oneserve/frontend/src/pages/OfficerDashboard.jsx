import { useState, useEffect } from 'react';
import { FileText, CheckCircle, Clock, TrendingUp } from 'lucide-react';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import StatCard from '../components/StatCard';
import { LineChartComponent, PieChartComponent } from '../components/Charts';
import api from '../api/axios';
import toast from 'react-hot-toast';

const OfficerDashboard = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await api.get('/dashboard/officer');
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

  const categoryData = Object.entries(stats?.category_trend || {}).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />
      
      <div className="flex">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />
        
        <main className="flex-1 p-6 lg:p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">Officer Dashboard</h1>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <StatCard
              title="Pending Complaints"
              value={stats?.pending_complaints || 0}
              icon={Clock}
              color="warning"
            />
            <StatCard
              title="In Progress"
              value={stats?.in_progress_complaints || 0}
              icon={TrendingUp}
              color="primary"
            />
            <StatCard
              title="Resolved"
              value={stats?.resolved_complaints || 0}
              icon={CheckCircle}
              color="success"
            />
            <StatCard
              title="Avg Resolution Time"
              value={`${stats?.avg_resolution_time || 0}h`}
              icon={FileText}
              color="purple"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {stats?.monthly_resolutions && stats.monthly_resolutions.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Monthly Resolutions
                </h3>
                <LineChartComponent 
                  data={stats.monthly_resolutions} 
                  xAxisKey="month" 
                  dataKey="count" 
                />
              </div>
            )}

            {categoryData.length > 0 && (
              <div className="card">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Category Distribution
                </h3>
                <PieChartComponent data={categoryData} />
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default OfficerDashboard;
