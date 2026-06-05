import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Upload, FileText } from "lucide-react";
import Navbar from "../../components/Navbar";
import Sidebar from "../../components/Sidebar";
import api from "../../api/axios";
import toast from "react-hot-toast";

const ComplaintCreate = () => {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const [formData, setFormData] = useState({
    title: "",
    description: "",
    place: "",
  });

  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  // ✅ This helps to re-select the SAME file again
  const [fileInputKey, setFileInputKey] = useState(Date.now());

  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleImageChange = (e) => {
    if (!e.target.files || !e.target.files[0]) return;

    const file = e.target.files[0];

    // ✅ Validate file type
    if (!file.type.startsWith("image/")) {
      toast.error("Please upload a valid image file");
      return;
    }

    // ✅ Validate size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      toast.error("Image must be under 10MB");
      return;
    }

    setImage(file);

    // ✅ Create preview URL
    const previewUrl = URL.createObjectURL(file);
    setImagePreview(previewUrl);
  };

  const removeImage = () => {
    // ✅ Clear image state
    setImage(null);

    // ✅ Revoke old preview URL
    if (imagePreview) URL.revokeObjectURL(imagePreview);
    setImagePreview(null);

    // ✅ Reset input so same file can be selected again
    setFileInputKey(Date.now());
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    // ✅ Validation: at least one field must be present
    if (!formData.title?.trim() && !formData.description?.trim() && !image) {
      toast.error("Please provide at least title, description, or image");
      return;
    }

    setLoading(true);

    try {
      const data = new FormData();

      if (formData.title?.trim()) data.append("title", formData.title.trim());
      if (formData.description?.trim())
        data.append("description", formData.description.trim());
      if (formData.place?.trim()) data.append("place", formData.place.trim());
      if (image) data.append("image", image);

      await api.post("/complaints/create", data, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      toast.success("Complaint registered successfully!");
      navigate("/complaints");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Error creating complaint");
    } finally {
      setLoading(false);
    }
  };

  // ✅ Cleanup preview URL on component unmount
  useEffect(() => {
    return () => {
      if (imagePreview) URL.revokeObjectURL(imagePreview);
    };
  }, [imagePreview]);

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

      <div className="flex flex-1 overflow-hidden">
        <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-6xl mx-auto">
            <div className="mb-8">
              <h1 className="text-3xl font-bold text-gray-900">
                File a Complaint
              </h1>
              <p className="text-gray-600 mt-1">
                Report an issue and we&apos;ll assign it to the right department
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* ================= LEFT FORM ================= */}
              <div className="lg:col-span-2">
                <div className="card">
                  <form onSubmit={handleSubmit} className="space-y-6">
                    {/* Title */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Title (Optional)
                      </label>
                      <input
                        type="text"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        className="input-field"
                        placeholder="Brief title of your complaint"
                      />
                    </div>

                    {/* Description */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Description (Optional)
                      </label>
                      <textarea
                        name="description"
                        value={formData.description}
                        onChange={handleChange}
                        rows={5}
                        className="input-field"
                        placeholder="Describe the issue in detail..."
                      />
                    </div>

                    {/* Place */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Location/Place (Optional)
                      </label>
                      <input
                        type="text"
                        name="place"
                        value={formData.place}
                        onChange={handleChange}
                        className="input-field"
                        placeholder="Where is the issue located?"
                      />
                    </div>

                    {/* Upload image */}
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Upload Image (Optional)
                      </label>

                      <div className="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-lg hover:border-primary-400 transition-colors">
                        <div className="space-y-1 text-center">
                          <Upload className="mx-auto h-12 w-12 text-gray-400" />

                          <div className="flex text-sm text-gray-600 justify-center">
                            <label className="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500">
                              <span>Upload a file</span>
                              <input
                                key={fileInputKey}
                                type="file"
                                className="sr-only"
                                accept="image/*"
                                onChange={handleImageChange}
                              />
                            </label>
                            <p className="pl-1">or drag and drop</p>
                          </div>

                          <p className="text-xs text-gray-500">
                            PNG, JPG, JPEG up to 10MB
                          </p>

                          {image && (
                            <p className="text-sm text-green-600 font-medium">
                              Selected: {image.name}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Note */}
                    <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded">
                      <div className="flex">
                        <FileText className="h-5 w-5 text-yellow-400 mt-0.5" />
                        <div className="ml-3">
                          <p className="text-sm text-yellow-700">
                            <strong>Note:</strong> At least one field (title,
                            description, or image) must be provided. If you
                            upload an image, we&apos;ll automatically detect and
                            assign it to the relevant department.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Buttons */}
                    <div className="flex gap-4">
                      <button
                        type="submit"
                        disabled={loading}
                        className="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {loading ? "Submitting..." : "Submit Complaint"}
                      </button>

                      <button
                        type="button"
                        onClick={() => navigate("/complaints")}
                        className="btn-secondary"
                      >
                        Cancel
                      </button>
                    </div>
                  </form>
                </div>
              </div>

              {/* ================= RIGHT PREVIEW ================= */}
              <div className="lg:col-span-1">
                <div className="card sticky top-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">
                    Image Preview
                  </h3>

                  {imagePreview ? (
                    <div className="space-y-4">
                      <img
                        src={imagePreview}
                        alt="Complaint preview"
                        className="w-full h-auto rounded-lg border border-gray-200"
                      />

                      <button
                        type="button"
                        onClick={removeImage}
                        className="w-full btn-secondary text-sm"
                      >
                        Remove Image
                      </button>
                    </div>
                  ) : (
                    <div className="flex items-center justify-center h-64 bg-gray-100 rounded-lg border-2 border-dashed border-gray-300">
                      <div className="text-center text-gray-400">
                        <Upload className="h-12 w-12 mx-auto mb-2" />
                        <p className="text-sm">No image selected</p>
                        <p className="text-xs mt-1">
                          Upload an image to see preview
                        </p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
              {/* ================= END GRID ================= */}
            </div>
          </div>
        </main>
      </div>
    </div>
  );
};

export default ComplaintCreate;
