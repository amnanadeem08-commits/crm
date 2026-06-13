import React from "react";
import { Navigate } from "react-router-dom";

import { AuthContext } from "./context";

export function ProtectedRoute({ children }) {
  const { token } = React.useContext(AuthContext);
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

