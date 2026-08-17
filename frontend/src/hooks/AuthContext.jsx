import { createContext, useState, useEffect } from 'react';
import { login as apiLogin, register as apiRegister } from '../services/api';
import { jwtDecode } from 'jwt-decode';

export const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const decoded = jwtDecode(token);
        if (decoded.exp * 1000 < Date.now()) {
          logout();
        } else {
          setUser({ email: decoded.sub, role: decoded.role, id: decoded.user_id });
        }
      } catch (err) {
        logout();
      }
    }
    setLoading(false);
  }, []);

  const login = async (email, password) => {
    // Convert to URL-encoded form data for OAuth2
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);
    
    const { data } = await apiLogin(formData);
    localStorage.setItem('token', data.access_token);
    
    const decoded = jwtDecode(data.access_token);
    setUser({ email: decoded.sub, role: decoded.role, id: decoded.user_id });
  };

  const register = async (email, password) => {
    await apiRegister({ email, password });
    await login(email, password);
  };

  const logout = () => {
    localStorage.removeItem('token');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};
