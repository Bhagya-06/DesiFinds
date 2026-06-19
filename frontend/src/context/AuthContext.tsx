import React, { createContext, useContext, useState, useEffect } from "react";

interface User {
  username: string;
}

interface AuthContextType {
  currentUser: User | null;
  login: (username: string, password: string) => Promise<boolean>;
  signup: (username: string, password: string) => Promise<boolean>;
  logout: () => void;
  authModalOpen: boolean;
  setAuthModalOpen: (open: boolean) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [authModalOpen, setAuthModalOpen] = useState(false);

  useEffect(() => {
    // Load current session
    try {
      const stored = localStorage.getItem("desifinds_current_user");
      if (stored) {
        setCurrentUser(JSON.parse(stored));
      }
    } catch {
      localStorage.removeItem("desifinds_current_user");
    }
  }, []);

  const login = async (username: string, password: string): Promise<boolean> => {
    try {
      const trimmedUser = username.trim().toLowerCase();
      if (!trimmedUser || !password) return false;

      const usersRaw = localStorage.getItem("desifinds_users");
      const users = usersRaw ? JSON.parse(usersRaw) : {};

      if (users[trimmedUser] && users[trimmedUser] === password) {
        const userObj = { username: username.trim() };
        setCurrentUser(userObj);
        localStorage.setItem("desifinds_current_user", JSON.stringify(userObj));
        return true;
      }
      return false;
    } catch {
      return false;
    }
  };

  const signup = async (username: string, password: string): Promise<boolean> => {
    try {
      const trimmedUser = username.trim().toLowerCase();
      if (!trimmedUser || !password) return false;

      const usersRaw = localStorage.getItem("desifinds_users");
      const users = usersRaw ? JSON.parse(usersRaw) : {};

      if (users[trimmedUser]) {
        // User already exists
        return false;
      }

      users[trimmedUser] = password;
      localStorage.setItem("desifinds_users", JSON.stringify(users));

      // Auto login after signup
      const userObj = { username: username.trim() };
      setCurrentUser(userObj);
      localStorage.setItem("desifinds_current_user", JSON.stringify(userObj));
      return true;
    } catch {
      return false;
    }
  };

  const logout = () => {
    setCurrentUser(null);
    localStorage.removeItem("desifinds_current_user");
  };

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        login,
        signup,
        logout,
        authModalOpen,
        setAuthModalOpen,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
