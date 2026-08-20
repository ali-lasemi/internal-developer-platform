import {
  Activity,
  ArrowRight,
  Boxes,
  CheckCircle2,
  ChevronRight,
  CircleGauge,
  Cloud,
  Code2,
  Command,
  ExternalLink,
  FileCode2,
  GitBranch,
  Home,
  Layers3,
  LoaderCircle,
  LogOut,
  Menu,
  Plus,
  Search,
  ServerCog,
  ShieldCheck,
  Sparkles,
  Workflow,
  X,
  XCircle,
} from "lucide-react";

import {
  FormEvent,
  ReactNode,
  useEffect,
  useMemo,
  useState,
} from "react";

import {
  Link,
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";

import {
  Identity,
  clearSession,
  currentIdentity,
  getSession,
  login,
  logout,
  portalGet,
  portalPost,
} from "./api";

type Json = Record<
  string,
  any
>;

type ServiceRecord = {
  id: number;
  name: string;
  owner?: string;
  repository?: string;
  description?: string;
  lifecycle?: string;
  lifecycle_history?: Array<
    Json
  >;
};

type TemplateRecord = {
  name: string;
  version?: string;
  type?: string;
  description?: string;
};

function cx(
  ...values: Array<
    string | false | null | undefined
  >
) {
  return values
    .filter(Boolean)
    .join(" ");
}

function humanize(
  value?: string
) {
  if (!value) {
    return "Unknown";
  }

  return value
    .replace(/[-_]/g, " ")
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}

function lifecycleTone(
  lifecycle?: string
) {
  switch (lifecycle) {
    case "production":
      return "green";

    case "staging":
      return "purple";

    case "development":
      return "blue";

    case "deprecated":
    case "retired":
      return "muted";

    default:
      return "amber";
  }
}

function StatusPill({
  value,
}: {
  value?: string;
}) {
  return (
    <span
      className={cx(
        "status-pill",
        `tone-${lifecycleTone(
          value
        )}`
      )}
    >
      <span className="status-dot" />
      {humanize(value)}
    </span>
  );
}

function LoadingState() {
  return (
    <div className="state-card">
      <LoaderCircle className="spin" />
      <div>
        <strong>
          Loading workspace
        </strong>
        <p>
          Fetching the latest
          platform state.
        </p>
      </div>
    </div>
  );
}

function ErrorState({
  message,
}: {
  message: string;
}) {
  return (
    <div className="state-card error-state">
      <XCircle />
      <div>
        <strong>
          Something went wrong
        </strong>
        <p>{message}</p>
      </div>
    </div>
  );
}

function EmptyState({
  title,
  description,
  action,
}: {
  title: string;
  description: string;
  action?: ReactNode;
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">
        <Boxes />
      </div>
      <h3>{title}</h3>
      <p>{description}</p>
      {action}
    </div>
  );
}

function SectionHeader({
  eyebrow,
  title,
  description,
  action,
}: {
  eyebrow?: string;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="section-header">
      <div>
        {eyebrow && (
          <span className="eyebrow">
            {eyebrow}
          </span>
        )}

        <h1>{title}</h1>

        {description && (
          <p>{description}</p>
        )}
      </div>

      {action && (
        <div className="section-action">
          {action}
        </div>
      )}
    </div>
  );
}

function MetricCard({
  label,
  value,
  hint,
  icon,
}: {
  label: string;
  value: ReactNode;
  hint?: string;
  icon: ReactNode;
}) {
  return (
    <article className="metric-card">
      <div className="metric-top">
        <span className="metric-icon">
          {icon}
        </span>
        <span className="metric-label">
          {label}
        </span>
      </div>

      <strong className="metric-value">
        {value}
      </strong>

      {hint && (
        <span className="metric-hint">
          {hint}
        </span>
      )}
    </article>
  );
}

function LoginPage({
  onAuthenticated,
}: {
  onAuthenticated: (
    identity: Identity
  ) => void;
}) {
  const navigate =
    useNavigate();

  const [username, setUsername] =
    useState("");

  const [password, setPassword] =
    useState("");

  const [busy, setBusy] =
    useState(false);

  const [error, setError] =
    useState("");

  async function submit(
    event: FormEvent
  ) {
    event.preventDefault();
    setBusy(true);
    setError("");

    try {
      await login(
        username,
        password
      );

      const identity =
        await currentIdentity();

      onAuthenticated(identity);

      navigate("/");
    } catch (exception) {
      clearSession();

      setError(
        exception instanceof Error
          ? exception.message
          : "Authentication failed"
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <section className="auth-brand">
        <div className="brand-mark large">
          <Command />
        </div>

        <span className="eyebrow">
          Internal Developer
          Platform
        </span>

        <h1>
          Ship software without
          fighting the platform.
        </h1>

        <p>
          One product for service
          creation, ownership,
          delivery, reliability and
          engineering standards.
        </p>

        <div className="auth-features">
          <span>
            <CheckCircle2 />
            Self-service workflows
          </span>

          <span>
            <CheckCircle2 />
            Golden path templates
          </span>

          <span>
            <CheckCircle2 />
            Reliability and quality
            gates
          </span>
        </div>
      </section>

      <section className="auth-panel-wrap">
        <form
          className="auth-panel"
          onSubmit={submit}
        >
          <div>
            <span className="eyebrow">
              Platform Console
            </span>

            <h2>
              Welcome back
            </h2>

            <p className="muted">
              Sign in with your
              platform identity.
            </p>
          </div>

          <label>
            Username

            <input
              autoFocus
              required
              value={username}
              onChange={(event) =>
                setUsername(
                  event.target.value
                )
              }
              placeholder="developer"
            />
          </label>

          <label>
            Password

            <input
              required
              type="password"
              value={password}
              onChange={(event) =>
                setPassword(
                  event.target.value
                )
              }
              placeholder="????????"
            />
          </label>

          {error && (
            <div className="inline-error">
              {error}
            </div>
          )}

          <button
            className="button primary wide"
            disabled={busy}
            type="submit"
          >
            {busy ? (
              <>
                <LoaderCircle
                  className="spin"
                />
                Signing in
              </>
            ) : (
              <>
                Sign in
                <ArrowRight />
              </>
            )}
          </button>
        </form>
      </section>
    </main>
  );
}

const navigation = [
  {
    to: "/",
    label: "Home",
    icon: Home,
  },
  {
    to: "/services",
    label: "Services",
    icon: Boxes,
  },
  {
    to: "/templates",
    label: "Templates",
    icon: Layers3,
  },
  {
    to: "/create",
    label: "Create service",
    icon: Plus,
  },
];

function ProductShell({
  identity,
  onLogout,
}: {
  identity: Identity;
  onLogout: () => void;
}) {
  const [
    mobileOpen,
    setMobileOpen,
  ] = useState(false);

  return (
    <div className="product-shell">
      <aside
        className={cx(
          "sidebar",
          mobileOpen &&
            "sidebar-open"
        )}
      >
        <div className="sidebar-header">
          <Link
            to="/"
            className="brand"
          >
            <span className="brand-mark">
              <Command />
            </span>

            <span>
              <strong>
                Platform
              </strong>
              <small>
                Developer Console
              </small>
            </span>
          </Link>

          <button
            className="icon-button mobile-only"
            onClick={() =>
              setMobileOpen(false)
            }
          >
            <X />
          </button>
        </div>

        <nav className="main-nav">
          <span className="nav-label">
            Workspace
          </span>

          {navigation.map(
            ({
              to,
              label,
              icon: Icon,
            }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({
                  isActive,
                }) =>
                  cx(
                    "nav-link",
                    isActive &&
                      "active"
                  )
                }
                onClick={() =>
                  setMobileOpen(
                    false
                  )
                }
              >
                <Icon />
                {label}
              </NavLink>
            )
          )}
        </nav>

        <div className="sidebar-footer">
          <div className="identity-card">
            <div className="avatar">
              {identity.username
                .slice(0, 2)
                .toUpperCase()}
            </div>

            <div>
              <strong>
                {identity.username}
              </strong>
              <span>
                {identity.team}
              </span>
            </div>
          </div>

          <button
            className="nav-link logout-button"
            onClick={onLogout}
          >
            <LogOut />
            Sign out
          </button>
        </div>
      </aside>

      <div className="content-shell">
        <header className="topbar">
          <button
            className="icon-button mobile-only"
            onClick={() =>
              setMobileOpen(true)
            }
          >
            <Menu />
          </button>

          <div className="topbar-context">
            <span className="health-dot" />
            Platform workspace
          </div>

          <div className="topbar-user">
            <span>
              {identity.role}
            </span>
          </div>
        </header>

        <main className="content">
          <Routes>
            <Route
              path="/"
              element={
                <DashboardPage
                  identity={
                    identity
                  }
                />
              }
            />

            <Route
              path="/services"
              element={
                <ServicesPage />
              }
            />

            <Route
              path="/services/:serviceId"
              element={
                <ServicePage />
              }
            />

            <Route
              path="/templates"
              element={
                <TemplatesPage />
              }
            />

            <Route
              path="/create"
              element={
                <CreateServicePage
                  identity={
                    identity
                  }
                />
              }
            />

            <Route
              path="*"
              element={
                <Navigate
                  to="/"
                  replace
                />
              }
            />
          </Routes>
        </main>
      </div>
    </div>
  );
}

function DashboardPage({
  identity,
}: {
  identity: Identity;
}) {
  const [data, setData] =
    useState<Json | null>(
      null
    );

  const [error, setError] =
    useState("");

  useEffect(() => {
    portalGet<Json>(
      "/portal/dashboard"
    )
      .then(setData)
      .catch((exception) =>
        setError(
          exception instanceof Error
            ? exception.message
            : "Unable to load dashboard"
        )
      );
  }, []);

  if (error) {
    return (
      <ErrorState
        message={error}
      />
    );
  }

  if (!data) {
    return <LoadingState />;
  }

  const totals =
    data.totals ?? {};

  const services:
    ServiceRecord[] =
      data.services ?? [];

  const workflows:
    Json[] =
      data.workflows ?? [];

  return (
    <>
      <SectionHeader
        eyebrow="Developer workspace"
        title={`Good to see you, ${identity.username}`}
        description="Everything you need to create, understand and operate your services."
        action={
          <Link
            to="/create"
            className="button primary"
          >
            <Plus />
            Create service
          </Link>
        }
      />

      <section className="metric-grid">
        <MetricCard
          label="Services"
          value={
            totals.services ?? 0
          }
          hint={`${totals.production_services ?? 0} in production`}
          icon={<Boxes />}
        />

        <MetricCard
          label="Workflow runs"
          value={
            totals.workflow_executions ??
            0
          }
          hint={`${totals.failed_workflows ?? 0} failed`}
          icon={<Workflow />}
        />

        <MetricCard
          label="Golden paths"
          value={
            totals.templates ?? 0
          }
          hint="Ready to provision"
          icon={<Sparkles />}
        />

        <MetricCard
          label="Platform"
          value={humanize(
            data.platform?.status
          )}
          hint={`${data.platform?.healthy_services ?? 0}/${data.platform?.total_services ?? 0} systems healthy`}
          icon={<CircleGauge />}
        />
      </section>

      <section className="dashboard-grid">
        <article className="panel span-2">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                Your platform
              </span>
              <h2>
                Recent services
              </h2>
            </div>

            <Link
              to="/services"
              className="text-link"
            >
              View catalog
              <ChevronRight />
            </Link>
          </div>

          {services.length ? (
            <div className="service-list">
              {services
                .slice(0, 6)
                .map(
                  (service) => (
                    <Link
                      key={
                        service.id
                      }
                      to={`/services/${service.id}`}
                      className="service-row"
                    >
                      <div className="service-symbol">
                        <Code2 />
                      </div>

                      <div className="service-primary">
                        <strong>
                          {
                            service.name
                          }
                        </strong>
                        <span>
                          {service.owner ??
                            "Unowned"}
                        </span>
                      </div>

                      <StatusPill
                        value={
                          service.lifecycle
                        }
                      />

                      <ChevronRight className="chevron" />
                    </Link>
                  )
                )}
            </div>
          ) : (
            <EmptyState
              title="No services yet"
              description="Create your first service from a golden path."
              action={
                <Link
                  className="button primary"
                  to="/create"
                >
                  Create service
                </Link>
              }
            />
          )}
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                Automation
              </span>
              <h2>
                Recent runs
              </h2>
            </div>
          </div>

          <div className="activity-list">
            {workflows
              .slice(0, 6)
              .map(
                (workflow) => (
                  <div
                    key={
                      workflow.execution_id
                    }
                    className="activity-row"
                  >
                    <span
                      className={cx(
                        "activity-status",
                        workflow.status ===
                          "failed"
                          ? "failed"
                          : "success"
                      )}
                    >
                      {workflow.status ===
                      "failed" ? (
                        <XCircle />
                      ) : (
                        <CheckCircle2 />
                      )}
                    </span>

                    <div>
                      <strong>
                        {humanize(
                          workflow.workflow
                        )}
                      </strong>
                      <span>
                        {workflow.service_name ??
                          "Platform workflow"}
                      </span>
                    </div>
                  </div>
                )
              )}

            {!workflows.length && (
              <p className="muted">
                No workflow runs yet.
              </p>
            )}
          </div>
        </article>
      </section>
    </>
  );
}

function ServicesPage() {
  const [
    services,
    setServices,
  ] = useState<
    ServiceRecord[]
  >([]);

  const [query, setQuery] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  const [error, setError] =
    useState("");

  useEffect(() => {
    portalGet<{
      services: ServiceRecord[];
    }>("/portal/services")
      .then((payload) =>
        setServices(
          payload.services ?? []
        )
      )
      .catch((exception) =>
        setError(
          exception instanceof Error
            ? exception.message
            : "Unable to load services"
        )
      )
      .finally(() =>
        setLoading(false)
      );
  }, []);

  const filtered = useMemo(
    () => {
      const value =
        query
          .trim()
          .toLowerCase();

      if (!value) {
        return services;
      }

      return services.filter(
        (service) =>
          [
            service.name,
            service.owner,
            service.lifecycle,
            service.description,
          ].some((field) =>
            field
              ?.toLowerCase()
              .includes(value)
          )
      );
    },
    [query, services]
  );

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <ErrorState
        message={error}
      />
    );
  }

  return (
    <>
      <SectionHeader
        eyebrow="Service catalog"
        title="Services"
        description="Discover ownership, lifecycle and engineering health across the platform."
        action={
          <Link
            to="/create"
            className="button primary"
          >
            <Plus />
            Create service
          </Link>
        }
      />

      <div className="toolbar">
        <div className="search-field">
          <Search />
          <input
            value={query}
            onChange={(event) =>
              setQuery(
                event.target.value
              )
            }
            placeholder="Search services, owners or lifecycle..."
          />
        </div>

        <span className="result-count">
          {filtered.length}{" "}
          service
          {filtered.length === 1
            ? ""
            : "s"}
        </span>
      </div>

      {filtered.length ? (
        <section className="catalog-grid">
          {filtered.map(
            (service) => (
              <Link
                key={service.id}
                to={`/services/${service.id}`}
                className="service-card"
              >
                <div className="service-card-top">
                  <span className="service-symbol large">
                    <Code2 />
                  </span>

                  <StatusPill
                    value={
                      service.lifecycle
                    }
                  />
                </div>

                <div>
                  <h3>
                    {service.name}
                  </h3>

                  <p>
                    {service.description ||
                      "No service description yet."}
                  </p>
                </div>

                <div className="card-meta">
                  <span>
                    <ServerCog />
                    {service.owner ||
                      "Unowned"}
                  </span>

                  {service.repository && (
                    <span>
                      <GitBranch />
                      Repository linked
                    </span>
                  )}
                </div>

                <div className="card-footer">
                  <span>
                    Open service
                  </span>

                  <ArrowRight />
                </div>
              </Link>
            )
          )}
        </section>
      ) : (
        <EmptyState
          title="No matching services"
          description="Try another search or create a new service."
        />
      )}
    </>
  );
}

function ServicePage() {
  const { serviceId } =
    useParams();

  const [service, setService] =
    useState<
      ServiceRecord | null
    >(null);

  const [
    scorecard,
    setScorecard,
  ] = useState<Json | null>(
    null
  );

  const [
    qualityGate,
    setQualityGate,
  ] = useState<Json | null>(
    null
  );

  const [error, setError] =
    useState("");

  useEffect(() => {
    if (!serviceId) {
      return;
    }

    Promise.all([
      portalGet<ServiceRecord>(
        `/portal/services/${serviceId}`
      ),
      portalGet<Json>(
        `/portal/services/${serviceId}/scorecard`
      ),
      portalGet<Json>(
        `/portal/services/${serviceId}/quality-gate`
      ),
    ])
      .then(
        ([
          serviceResult,
          scoreResult,
          gateResult,
        ]) => {
          setService(
            serviceResult
          );
          setScorecard(
            scoreResult
          );
          setQualityGate(
            gateResult
          );
        }
      )
      .catch((exception) =>
        setError(
          exception instanceof Error
            ? exception.message
            : "Unable to load service"
        )
      );
  }, [serviceId]);

  if (error) {
    return (
      <ErrorState
        message={error}
      />
    );
  }

  if (!service) {
    return <LoadingState />;
  }

  const checks: Record<
    string,
    {
      passed: boolean;
      weight: number;
    }
  > =
    scorecard?.checks ?? {};

  const history =
    service.lifecycle_history ??
    [];

  return (
    <>
      <div className="service-heading">
        <div className="service-title-wrap">
          <span className="service-symbol hero">
            <Code2 />
          </span>

          <div>
            <div className="breadcrumb">
              <Link to="/services">
                Services
              </Link>
              <ChevronRight />
              <span>
                {service.name}
              </span>
            </div>

            <h1>
              {service.name}
            </h1>

            <div className="service-heading-meta">
              <StatusPill
                value={
                  service.lifecycle
                }
              />

              <span>
                Owned by{" "}
                <strong>
                  {service.owner ??
                    "Unowned"}
                </strong>
              </span>
            </div>
          </div>
        </div>

        {service.repository && (
          <a
            href={
              service.repository
            }
            target="_blank"
            rel="noreferrer"
            className="button secondary"
          >
            <GitBranch />
            Repository
            <ExternalLink />
          </a>
        )}
      </div>

      <section className="metric-grid compact">
        <MetricCard
          label="Quality score"
          value={
            scorecard?.score ??
            "?"
          }
          hint={
            scorecard?.grade
              ? `Grade ${scorecard.grade}`
              : "Not evaluated"
          }
          icon={
            <ShieldCheck />
          }
        />

        <MetricCard
          label="Quality gate"
          value={
            qualityGate?.passed
              ? "Passing"
              : "Blocked"
          }
          hint="Engineering standards"
          icon={<CircleGauge />}
        />

        <MetricCard
          label="Lifecycle"
          value={humanize(
            service.lifecycle
          )}
          hint={`${history.length} recorded transitions`}
          icon={<Workflow />}
        />

        <MetricCard
          label="Ownership"
          value={
            service.owner ||
            "Unowned"
          }
          hint="Accountable team"
          icon={<ServerCog />}
        />
      </section>

      <section className="detail-grid">
        <article className="panel span-2">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                Service overview
              </span>
              <h2>
                Engineering context
              </h2>
            </div>
          </div>

          <dl className="detail-list">
            <div>
              <dt>
                Description
              </dt>
              <dd>
                {service.description ||
                  "No description provided."}
              </dd>
            </div>

            <div>
              <dt>
                Owner
              </dt>
              <dd>
                {service.owner ||
                  "Unowned"}
              </dd>
            </div>

            <div>
              <dt>
                Repository
              </dt>
              <dd>
                {service.repository ? (
                  <a
                    href={
                      service.repository
                    }
                    target="_blank"
                    rel="noreferrer"
                  >
                    {
                      service.repository
                    }
                  </a>
                ) : (
                  "Not linked"
                )}
              </dd>
            </div>
          </dl>
        </article>

        <article className="panel">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                Scorecard
              </span>
              <h2>
                Standards
              </h2>
            </div>
          </div>

          <div className="check-list">
            {Object.entries(
              checks
            ).map(
              ([
                name,
                check,
              ]) => (
                <div
                  key={name}
                  className="check-row"
                >
                  {check.passed ? (
                    <CheckCircle2 className="success-icon" />
                  ) : (
                    <XCircle className="danger-icon" />
                  )}

                  <span>
                    {humanize(
                      name
                    )}
                  </span>

                  <strong>
                    {check.weight}%
                  </strong>
                </div>
              )
            )}

            {!Object.keys(
              checks
            ).length && (
              <p className="muted">
                No scorecard
                data available.
              </p>
            )}
          </div>
        </article>

        <article className="panel span-3">
          <div className="panel-header">
            <div>
              <span className="eyebrow">
                Lifecycle
              </span>
              <h2>
                Service history
              </h2>
            </div>
          </div>

          {history.length ? (
            <div className="timeline">
              {history.map(
                (
                  event,
                  index
                ) => (
                  <div
                    className="timeline-item"
                    key={
                      event.id ??
                      index
                    }
                  >
                    <span className="timeline-dot" />

                    <div>
                      <strong>
                        {humanize(
                          event.to_state ??
                            event.lifecycle ??
                            event.status
                        )}
                      </strong>

                      <span>
                        {event.created_at ??
                          event.changed_at ??
                          "Recorded lifecycle event"}
                      </span>
                    </div>
                  </div>
                )
              )}
            </div>
          ) : (
            <p className="muted">
              No lifecycle history
              recorded yet.
            </p>
          )}
        </article>
      </section>
    </>
  );
}

function TemplatesPage() {
  const [
    templates,
    setTemplates,
  ] = useState<
    TemplateRecord[]
  >([]);

  const [error, setError] =
    useState("");

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    portalGet<{
      templates: TemplateRecord[];
    }>("/portal/templates")
      .then((payload) =>
        setTemplates(
          payload.templates ?? []
        )
      )
      .catch((exception) =>
        setError(
          exception instanceof Error
            ? exception.message
            : "Unable to load templates"
        )
      )
      .finally(() =>
        setLoading(false)
      );
  }, []);

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return (
      <ErrorState
        message={error}
      />
    );
  }

  return (
    <>
      <SectionHeader
        eyebrow="Golden paths"
        title="Templates"
        description="Approved starting points that encode platform defaults and engineering standards."
        action={
          <Link
            to="/create"
            className="button primary"
          >
            <Plus />
            Create service
          </Link>
        }
      />

      <section className="template-grid">
        {templates.map(
          (template) => (
            <article
              key={
                template.name
              }
              className="template-card"
            >
              <div className="template-icon">
                <FileCode2 />
              </div>

              <span className="eyebrow">
                {humanize(
                  template.type ??
                    "Golden path"
                )}
              </span>

              <h3>
                {humanize(
                  template.name
                )}
              </h3>

              <p>
                {template.description ||
                  "Production-ready service foundation with platform standards built in."}
              </p>

              <div className="template-meta">
                Version{" "}
                {template.version ??
                  "1.0"}
              </div>

              <Link
                to={`/create?template=${encodeURIComponent(
                  template.name
                )}`}
                className="button secondary wide"
              >
                Use template
                <ArrowRight />
              </Link>
            </article>
          )
        )}
      </section>

      {!templates.length && (
        <EmptyState
          title="No templates available"
          description="Template registry is currently empty."
        />
      )}
    </>
  );
}

function CreateServicePage({
  identity,
}: {
  identity: Identity;
}) {
  const navigate =
    useNavigate();

  const [
    templates,
    setTemplates,
  ] = useState<
    TemplateRecord[]
  >([]);

  const [step, setStep] =
    useState(1);

  const [busy, setBusy] =
    useState(false);

  const [error, setError] =
    useState("");

  const [
    preview,
    setPreview,
  ] = useState<Json | null>(
    null
  );

  const [result, setResult] =
    useState<Json | null>(
      null
    );

  const [form, setForm] =
    useState({
      name: "",
      description: "",
      repository: "",
      template:
        "backend-service",
      environment:
        "development",
    });

  useEffect(() => {
    portalGet<{
      templates: TemplateRecord[];
    }>("/portal/templates")
      .then((payload) => {
        const values =
          payload.templates ?? [];

        setTemplates(values);

        if (
          values.length &&
          !values.some(
            (item) =>
              item.name ===
              form.template
          )
        ) {
          setForm(
            (current) => ({
              ...current,
              template:
                values[0].name,
            })
          );
        }
      })
      .catch(() => {
        // Form remains usable with the default golden path.
      });
  }, []);

  function update(
    name: string,
    value: string
  ) {
    setForm(
      (current) => ({
        ...current,
        [name]: value,
      })
    );
  }

  async function createPreview() {
    setBusy(true);
    setError("");

    try {
      const payload =
        await portalPost<Json>(
          `/portal/scaffolds/${form.template}/preview`,
          {
            name: form.name,
            owner:
              identity.team,
            repository:
              form.repository,
            environment:
              form.environment,
          }
        );

      setPreview(payload);
      setStep(3);
    } catch (exception) {
      setError(
        exception instanceof Error
          ? exception.message
          : "Preview failed"
      );
    } finally {
      setBusy(false);
    }
  }

  async function provision() {
    setBusy(true);
    setError("");

    try {
      const payload =
        await portalPost<Json>(
          "/portal/services/provision",
          {
            name: form.name,
            owner:
              identity.team,
            repository:
              form.repository,
            description:
              form.description,
            template:
              form.template,
            environment:
              form.environment,
          }
        );

      setResult(payload);
      setStep(4);
    } catch (exception) {
      setError(
        exception instanceof Error
          ? exception.message
          : "Provisioning failed"
      );
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <SectionHeader
        eyebrow="Self service"
        title="Create service"
        description="Start from a golden path and let the platform build the service foundation."
      />

      <div className="wizard-layout">
        <aside className="wizard-steps">
          {[
            [
              1,
              "Foundation",
              "Choose a golden path",
            ],
            [
              2,
              "Configuration",
              "Describe your service",
            ],
            [
              3,
              "Review",
              "Preview generated artifacts",
            ],
            [
              4,
              "Complete",
              "Provisioning result",
            ],
          ].map(
            ([
              number,
              title,
              description,
            ]) => (
              <div
                key={number}
                className={cx(
                  "wizard-step",
                  step === number &&
                    "current",
                  step >
                    Number(
                      number
                    ) &&
                    "complete"
                )}
              >
                <span className="step-number">
                  {step >
                  Number(number) ? (
                    <CheckCircle2 />
                  ) : (
                    number
                  )}
                </span>

                <div>
                  <strong>
                    {title}
                  </strong>
                  <span>
                    {description}
                  </span>
                </div>
              </div>
            )
          )}
        </aside>

        <section className="wizard-panel">
          {step === 1 && (
            <>
              <div className="wizard-heading">
                <span className="eyebrow">
                  Step 1 of 4
                </span>
                <h2>
                  Choose a golden
                  path
                </h2>
                <p>
                  Select the service
                  foundation that best
                  matches what you are
                  building.
                </p>
              </div>

              <div className="choice-grid">
                {(templates.length
                  ? templates
                  : [
                      {
                        name: "backend-service",
                        type: "service",
                        version:
                          "1.0",
                      },
                    ]
                ).map(
                  (template) => (
                    <button
                      key={
                        template.name
                      }
                      type="button"
                      className={cx(
                        "choice-card",
                        form.template ===
                          template.name &&
                          "selected"
                      )}
                      onClick={() =>
                        update(
                          "template",
                          template.name
                        )
                      }
                    >
                      <FileCode2 />

                      <div>
                        <strong>
                          {humanize(
                            template.name
                          )}
                        </strong>
                        <span>
                          Version{" "}
                          {template.version ??
                            "1.0"}
                        </span>
                      </div>

                      <span className="choice-check">
                        <CheckCircle2 />
                      </span>
                    </button>
                  )
                )}
              </div>

              <div className="wizard-actions">
                <span />
                <button
                  className="button primary"
                  onClick={() =>
                    setStep(2)
                  }
                >
                  Continue
                  <ArrowRight />
                </button>
              </div>
            </>
          )}

          {step === 2 && (
            <>
              <div className="wizard-heading">
                <span className="eyebrow">
                  Step 2 of 4
                </span>
                <h2>
                  Configure your
                  service
                </h2>
                <p>
                  Ownership is derived
                  from your platform
                  identity.
                </p>
              </div>

              <div className="form-grid">
                <label>
                  Service name
                  <input
                    value={
                      form.name
                    }
                    onChange={(
                      event
                    ) =>
                      update(
                        "name",
                        event.target
                          .value
                      )
                    }
                    placeholder="payments-api"
                  />
                </label>

                <label>
                  Owner
                  <input
                    disabled
                    value={
                      identity.team
                    }
                  />
                </label>

                <label className="span-2">
                  Description
                  <textarea
                    value={
                      form.description
                    }
                    onChange={(
                      event
                    ) =>
                      update(
                        "description",
                        event.target
                          .value
                      )
                    }
                    placeholder="What does this service do?"
                  />
                </label>

                <label className="span-2">
                  Repository URL
                  <input
                    value={
                      form.repository
                    }
                    onChange={(
                      event
                    ) =>
                      update(
                        "repository",
                        event.target
                          .value
                      )
                    }
                    placeholder="https://github.com/company/payments-api"
                  />
                </label>

                <label>
                  Environment
                  <select
                    value={
                      form.environment
                    }
                    onChange={(
                      event
                    ) =>
                      update(
                        "environment",
                        event.target
                          .value
                      )
                    }
                  >
                    <option value="development">
                      Development
                    </option>
                    <option value="staging">
                      Staging
                    </option>
                    <option value="production">
                      Production
                    </option>
                  </select>
                </label>
              </div>

              {error && (
                <div className="inline-error">
                  {error}
                </div>
              )}

              <div className="wizard-actions">
                <button
                  className="button ghost"
                  onClick={() =>
                    setStep(1)
                  }
                >
                  Back
                </button>

                <button
                  className="button primary"
                  disabled={
                    busy ||
                    form.name.length <
                      2 ||
                    !form.repository ||
                    !form.description
                  }
                  onClick={
                    createPreview
                  }
                >
                  {busy ? (
                    <LoaderCircle className="spin" />
                  ) : (
                    <Sparkles />
                  )}
                  Preview
                </button>
              </div>
            </>
          )}

          {step === 3 && (
            <>
              <div className="wizard-heading">
                <span className="eyebrow">
                  Step 3 of 4
                </span>

                <h2>
                  Review generated
                  foundation
                </h2>

                <p>
                  Verify what the
                  platform will create
                  before provisioning.
                </p>
              </div>

              <div className="preview-summary">
                <div>
                  <span>
                    Template
                  </span>
                  <strong>
                    {humanize(
                      preview?.template
                    )}
                  </strong>
                </div>

                <div>
                  <span>
                    Version
                  </span>
                  <strong>
                    {preview?.version ??
                      "?"}
                  </strong>
                </div>

                <div>
                  <span>
                    Files
                  </span>
                  <strong>
                    {preview?.files
                      ?.length ?? 0}
                  </strong>
                </div>

                <div>
                  <span>
                    Environment
                  </span>
                  <strong>
                    {humanize(
                      form.environment
                    )}
                  </strong>
                </div>
              </div>

              <div className="artifact-list">
                {(
                  preview?.files ??
                  []
                ).map(
                  (
                    file: string
                  ) => (
                    <div
                      key={file}
                      className="artifact-row"
                    >
                      <FileCode2 />
                      <code>
                        {file}
                      </code>
                    </div>
                  )
                )}
              </div>

              {error && (
                <div className="inline-error">
                  {error}
                </div>
              )}

              <div className="wizard-actions">
                <button
                  className="button ghost"
                  onClick={() =>
                    setStep(2)
                  }
                >
                  Back
                </button>

                <button
                  className="button primary"
                  disabled={busy}
                  onClick={provision}
                >
                  {busy ? (
                    <LoaderCircle className="spin" />
                  ) : (
                    <Cloud />
                  )}
                  Provision service
                </button>
              </div>
            </>
          )}

          {step === 4 && (
            <div className="completion">
              <span className="completion-icon">
                <CheckCircle2 />
              </span>

              <span className="eyebrow">
                Provisioning complete
              </span>

              <h2>
                {form.name} is now
                managed by the platform
              </h2>

              <p>
                The catalog,
                ownership, golden path
                and workflow execution
                were created
                successfully.
              </p>

              <div className="completion-meta">
                <span>
                  Status
                  <strong>
                    {humanize(
                      result?.status
                    )}
                  </strong>
                </span>

                <span>
                  Workflow
                  <strong>
                    {result?.workflow ??
                      "service-creation"}
                  </strong>
                </span>

                <span>
                  Environment
                  <strong>
                    {humanize(
                      result?.environment
                    )}
                  </strong>
                </span>
              </div>

              <div className="completion-actions">
                <button
                  className="button primary"
                  onClick={() =>
                    navigate(
                      "/services"
                    )
                  }
                >
                  Open service catalog
                  <ArrowRight />
                </button>

                <button
                  className="button secondary"
                  onClick={() => {
                    setStep(1);
                    setPreview(null);
                    setResult(null);
                    setForm({
                      name: "",
                      description: "",
                      repository: "",
                      template:
                        "backend-service",
                      environment:
                        "development",
                    });
                  }}
                >
                  Create another
                </button>
              </div>
            </div>
          )}
        </section>
      </div>
    </>
  );
}

export default function App() {
  const [
    identity,
    setIdentity,
  ] = useState<
    Identity | null
  >(null);

  const [loading, setLoading] =
    useState(true);

  useEffect(() => {
    if (!getSession()) {
      setLoading(false);
      return;
    }

    currentIdentity()
      .then(setIdentity)
      .catch(() => {
        clearSession();
        setIdentity(null);
      })
      .finally(() =>
        setLoading(false)
      );
  }, []);

  async function signOut() {
    await logout();
    setIdentity(null);
  }

  if (loading) {
    return (
      <div className="boot-screen">
        <div className="brand-mark large">
          <Command />
        </div>
        <LoaderCircle className="spin" />
      </div>
    );
  }

  if (!identity) {
    return (
      <Routes>
        <Route
          path="*"
          element={
            <LoginPage
              onAuthenticated={
                setIdentity
              }
            />
          }
        />
      </Routes>
    );
  }

  return (
    <ProductShell
      identity={identity}
      onLogout={signOut}
    />
  );
}
