import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "数据大屏",
  description: "移动优先的数据大屏页面",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
