"""All 25 Gravity ad format definitions with structured props for JSX rendering.

Each entry maps a style name to its description, SDK variant type, rendering
code (for search display), structured props (for themed JSX generation), and
list of ad fields the layout omits (i.e. does not display).

Structured fields:
    component:       "GravityAd" or "AdText"
    variant:         SDK variant prop (e.g. "card", "inline", "minimal")
    base_style:      dict of CSS-in-JS properties for the root style prop
    base_slot_props: dict of slot_name -> {css_prop: value} for slotProps
    extra_props:     dict of additional JSX props (showLabel, labelText, etc.)
"""

FORMAT_CATALOG: dict[str, dict] = {
    "card": {
        "name": "card",
        "description": "Standard card layout with header, body, and CTA button",
        "type": "card",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {},
        "base_slot_props": {},
        "extra_props": {},
        "code": '<GravityAd ad={ad} variant="card" />',
        "omits": [],
    },
    "floating": {
        "name": "floating",
        "description": "Elevated card with prominent shadow and hover lift effect",
        "type": "card",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "boxShadow": "0 8px 30px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)",
            "borderRadius": 14,
            "border": "none",
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    boxShadow: '0 8px 30px rgba(0,0,0,0.12), 0 2px 8px rgba(0,0,0,0.08)',
    borderRadius: 14,
    border: 'none',
  }}
/>""",
        "omits": [],
    },
    "glass": {
        "name": "glass",
        "description": "Frosted glass card with backdrop blur and translucent background",
        "type": "card",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "background": "rgba(255,255,255,0.6)",
            "backdropFilter": "blur(12px)",
            "WebkitBackdropFilter": "blur(12px)",
            "border": "1px solid rgba(255,255,255,0.3)",
            "boxShadow": "0 4px 16px rgba(0,0,0,0.06)",
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    background: 'rgba(255,255,255,0.6)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
    border: '1px solid rgba(255,255,255,0.3)',
    boxShadow: '0 4px 16px rgba(0,0,0,0.06)',
  }}
/>""",
        "omits": [],
    },
    "outlined": {
        "name": "outlined",
        "description": "Clean outlined card with no shadow — border only",
        "type": "card",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "boxShadow": "none",
            "border": "1.5px solid #E4E4E7",
            "borderRadius": 10,
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    boxShadow: 'none',
    border: '1.5px solid #E4E4E7',
    borderRadius: 10,
  }}
/>""",
        "omits": [],
    },
    "tinted": {
        "name": "tinted",
        "description": "Card with a soft tinted background color",
        "type": "card",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "background": "#F0F4FF",
            "border": "1px solid #DBEAFE",
            "boxShadow": "none",
        },
        "base_slot_props": {
            "cta": {"background": "#3B82F6"},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    background: '#F0F4FF',
    border: '1px solid #DBEAFE',
    boxShadow: 'none',
  }}
  slotProps={{
    cta: { style: { background: '#3B82F6' } },
  }}
/>""",
        "omits": [],
    },
    "accent": {
        "name": "accent",
        "description": "Card with a bold left accent border stripe",
        "type": "accent",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "borderLeft": "4px solid #2563EB",
            "borderRadius": "0 10px 10px 0",
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    borderLeft: '4px solid #2563EB',
    borderRadius: '0 10px 10px 0',
  }}
/>""",
        "omits": [],
    },
    "embed": {
        "name": "embed",
        "description": "Seamless embed that inherits parent container styles",
        "type": "embed",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "background": "transparent",
            "border": "none",
            "boxShadow": "none",
            "borderRadius": 0,
            "padding": 0,
        },
        "base_slot_props": {
            "inner": {"padding": "8px 0"},
            "cta": {"background": "#18181B", "borderRadius": 999},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    background: 'transparent',
    border: 'none',
    boxShadow: 'none',
    borderRadius: 0,
    padding: 0,
  }}
  slotProps={{
    inner: { style: { padding: '8px 0' } },
    cta: { style: { background: '#18181B', borderRadius: 999 } },
  }}
/>""",
        "omits": [],
    },
    "side-panel": {
        "name": "side-panel",
        "description": "Vertical panel layout designed for sidebar placement",
        "type": "side-panel",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "maxWidth": 280,
            "borderRadius": 12,
        },
        "base_slot_props": {
            "inner": {"padding": "16px", "gap": 12},
            "cta": {"alignSelf": "stretch", "textAlign": "center"},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    maxWidth: 280,
    borderRadius: 12,
  }}
  slotProps={{
    inner: { style: { padding: '16px', gap: 12 } },
    cta: { style: { alignSelf: 'stretch', textAlign: 'center' } },
  }}
/>""",
        "omits": [],
    },
    "split-action": {
        "name": "split-action",
        "description": "Two-column layout with content left and CTA right",
        "type": "split-action",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {},
        "base_slot_props": {
            "inner": {"alignItems": "center", "gap": 16, "padding": "14px 18px"},
            "cta": {"flexShrink": 0, "borderRadius": 8},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  slotProps={{
    inner: { style: { alignItems: 'center', gap: 16, padding: '14px 18px' } },
    cta: { style: { flexShrink: 0, borderRadius: 8 } },
  }}
/>""",
        "omits": [],
    },
    "labeled": {
        "name": "labeled",
        "description": "Prominent sponsored label above the ad content",
        "type": "labeled",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {},
        "base_slot_props": {
            "label": {
                "fontSize": 11,
                "fontWeight": 600,
                "color": "#2563EB",
                "border": "1px solid #BFDBFE",
                "background": "#EFF6FF",
                "padding": "3px 8px",
                "borderRadius": 4,
            },
        },
        "extra_props": {"showLabel": True, "labelText": "Sponsored"},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  showLabel={true}
  labelText="Sponsored"
  slotProps={{
    label: {
      style: {
        fontSize: 11,
        fontWeight: 600,
        color: '#2563EB',
        border: '1px solid #BFDBFE',
        background: '#EFF6FF',
        padding: '3px 8px',
        borderRadius: 4,
      },
    },
  }}
/>""",
        "omits": [],
    },
    "bubble": {
        "name": "bubble",
        "description": "Chat-bubble shaped card with rounded corners and tail",
        "type": "bubble",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "borderRadius": 18,
            "borderBottomLeftRadius": 4,
            "boxShadow": "0 2px 8px rgba(0,0,0,0.06)",
        },
        "base_slot_props": {
            "inner": {"padding": "14px 18px"},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    borderRadius: 18,
    borderBottomLeftRadius: 4,
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
  }}
  slotProps={{
    inner: { style: { padding: '14px 18px' } },
  }}
/>""",
        "omits": [],
    },
    "compact-bar": {
        "name": "compact-bar",
        "description": "Single-row inline bar — content left, CTA right",
        "type": "inline",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {},
        "base_slot_props": {
            "inner": {"padding": "10px 14px", "gap": 12},
            "body": {"gap": 0},
            "title": {"display": "none"},
            "cta": {"padding": "6px 14px", "fontSize": 12},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  showLabel={false}
  slotProps={{
    inner: { style: { padding: '10px 14px', gap: 12 } },
    body: { style: { gap: 0 } },
    title: { style: { display: 'none' } },
    cta: { style: { padding: '6px 14px', fontSize: 12 } },
  }}
/>""",
        "omits": ["title"],
    },
    "notification": {
        "name": "notification",
        "description": "Toast-style notification card with subtle entrance feel",
        "type": "notification",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "maxWidth": 360,
            "borderRadius": 12,
            "boxShadow": "0 4px 20px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06)",
            "border": "1px solid #E4E4E7",
        },
        "base_slot_props": {
            "inner": {"padding": "12px 16px", "gap": 8},
            "cta": {"fontSize": 12, "padding": "5px 12px"},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  style={{
    maxWidth: 360,
    borderRadius: 12,
    boxShadow: '0 4px 20px rgba(0,0,0,0.10), 0 1px 4px rgba(0,0,0,0.06)',
    border: '1px solid #E4E4E7',
  }}
  slotProps={{
    inner: { style: { padding: '12px 16px', gap: 8 } },
    cta: { style: { fontSize: 12, padding: '5px 12px' } },
  }}
/>""",
        "omits": [],
    },
    "tooltip": {
        "name": "tooltip",
        "description": "Compact tooltip-sized card for hover or inline reveal",
        "type": "tooltip",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "maxWidth": 260,
            "borderRadius": 8,
            "boxShadow": "0 4px 16px rgba(0,0,0,0.12)",
            "border": "1px solid #E4E4E7",
        },
        "base_slot_props": {
            "inner": {"padding": "10px 12px", "gap": 6},
            "title": {"fontSize": 13},
            "text": {"fontSize": 12},
            "cta": {"fontSize": 11, "padding": "4px 10px"},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  showLabel={false}
  style={{
    maxWidth: 260,
    borderRadius: 8,
    boxShadow: '0 4px 16px rgba(0,0,0,0.12)',
    border: '1px solid #E4E4E7',
  }}
  slotProps={{
    inner: { style: { padding: '10px 12px', gap: 6 } },
    title: { style: { fontSize: 13 } },
    text: { style: { fontSize: 12 } },
    cta: { style: { fontSize: 11, padding: '4px 10px' } },
  }}
/>""",
        "omits": [],
    },
    "banner": {
        "name": "banner",
        "description": "Full-width horizontal banner with inline layout",
        "type": "banner",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {
            "width": "100%",
            "borderRadius": 8,
            "background": "#FAFAFA",
            "border": "1px solid #E4E4E7",
        },
        "base_slot_props": {
            "inner": {"padding": "12px 20px", "gap": 16},
            "cta": {"flexShrink": 0},
        },
        "extra_props": {},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  style={{
    width: '100%',
    borderRadius: 8,
    background: '#FAFAFA',
    border: '1px solid #E4E4E7',
  }}
  slotProps={{
    inner: { style: { padding: '12px 20px', gap: 16 } },
    cta: { style: { flexShrink: 0 } },
  }}
/>""",
        "omits": [],
    },
    "toolbar": {
        "name": "toolbar",
        "description": "Slim toolbar-height bar for header or footer placement",
        "type": "toolbar",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {
            "borderRadius": 0,
            "border": "none",
            "borderBottom": "1px solid #E4E4E7",
            "background": "#FAFAFA",
        },
        "base_slot_props": {
            "inner": {"padding": "8px 16px", "gap": 12},
            "title": {"display": "none"},
            "text": {"fontSize": 12},
            "cta": {"fontSize": 11, "padding": "4px 12px"},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  showLabel={false}
  style={{
    borderRadius: 0,
    border: 'none',
    borderBottom: '1px solid #E4E4E7',
    background: '#FAFAFA',
  }}
  slotProps={{
    inner: { style: { padding: '8px 16px', gap: 12 } },
    title: { style: { display: 'none' } },
    text: { style: { fontSize: 12 } },
    cta: { style: { fontSize: 11, padding: '4px 12px' } },
  }}
/>""",
        "omits": ["title"],
    },
    "pill": {
        "name": "pill",
        "description": "Pill-shaped compact badge with rounded ends",
        "type": "pill",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {
            "borderRadius": 999,
            "display": "inline-flex",
            "border": "1px solid #E4E4E7",
        },
        "base_slot_props": {
            "inner": {"padding": "6px 8px 6px 16px", "gap": 10},
            "title": {"display": "none"},
            "text": {"fontSize": 12, "whiteSpace": "nowrap"},
            "cta": {"borderRadius": 999, "fontSize": 11, "padding": "4px 12px"},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  showLabel={false}
  style={{
    borderRadius: 999,
    display: 'inline-flex',
    border: '1px solid #E4E4E7',
  }}
  slotProps={{
    inner: { style: { padding: '6px 8px 6px 16px', gap: 10 } },
    title: { style: { display: 'none' } },
    text: { style: { fontSize: 12, whiteSpace: 'nowrap' } },
    cta: { style: { borderRadius: 999, fontSize: 11, padding: '4px 12px' } },
  }}
/>""",
        "omits": ["title"],
    },
    "divider": {
        "name": "divider",
        "description": "Inline ad that sits between content sections like a divider",
        "type": "divider",
        "component": "GravityAd",
        "variant": "inline",
        "base_style": {
            "background": "transparent",
            "border": "none",
            "boxShadow": "none",
            "borderTop": "1px solid #E4E4E7",
            "borderBottom": "1px solid #E4E4E7",
            "borderRadius": 0,
        },
        "base_slot_props": {
            "inner": {"padding": "10px 0", "gap": 12},
            "cta": {"background": "transparent", "color": "#2563EB", "border": "1px solid #2563EB", "fontSize": 12},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="inline"
  showLabel={false}
  style={{
    background: 'transparent',
    border: 'none',
    boxShadow: 'none',
    borderTop: '1px solid #E4E4E7',
    borderBottom: '1px solid #E4E4E7',
    borderRadius: 0,
  }}
  slotProps={{
    inner: { style: { padding: '10px 0', gap: 12 } },
    cta: { style: { background: 'transparent', color: '#2563EB', border: '1px solid #2563EB', fontSize: 12 } },
  }}
/>""",
        "omits": [],
    },
    "suggestion": {
        "name": "suggestion",
        "description": "Suggestion chip — looks like an AI suggestion or recommendation",
        "type": "suggestion",
        "component": "GravityAd",
        "variant": "card",
        "base_style": {
            "background": "#F4F4F5",
            "border": "1px solid #E4E4E7",
            "borderRadius": 12,
            "boxShadow": "none",
        },
        "base_slot_props": {
            "inner": {"padding": "12px 16px", "gap": 8},
            "title": {"display": "none"},
            "text": {"fontSize": 13, "color": "#3F3F46"},
            "cta": {"background": "#18181B", "borderRadius": 8, "fontSize": 12},
        },
        "extra_props": {"showLabel": False},
        "code": """\
<GravityAd
  ad={ad}
  variant="card"
  showLabel={false}
  style={{
    background: '#F4F4F5',
    border: '1px solid #E4E4E7',
    borderRadius: 12,
    boxShadow: 'none',
  }}
  slotProps={{
    inner: { style: { padding: '12px 16px', gap: 8 } },
    title: { style: { display: 'none' } },
    text: { style: { fontSize: 13, color: '#3F3F46' } },
    cta: { style: { background: '#18181B', borderRadius: 8, fontSize: 12 } },
  }}
/>""",
        "omits": ["title"],
    },
    "native": {
        "name": "native",
        "description": "Fully transparent native ad that blends with surrounding content",
        "type": "native",
        "component": "GravityAd",
        "variant": "minimal",
        "base_style": {},
        "base_slot_props": {
            "label": {
                "fontSize": 9,
                "color": "#A1A1AA",
                "border": "none",
                "padding": 0,
                "marginLeft": 0,
            },
        },
        "extra_props": {"showLabel": True, "labelText": "Sponsored"},
        "code": """\
<GravityAd
  ad={ad}
  variant="minimal"
  showLabel={true}
  labelText="Sponsored"
  slotProps={{
    label: {
      style: {
        fontSize: 9,
        color: '#A1A1AA',
        border: 'none',
        padding: 0,
        marginLeft: 0,
      },
    },
  }}
/>""",
        "omits": ["cta"],
    },
    "quote": {
        "name": "quote",
        "description": "Blockquote-styled ad with left border accent",
        "type": "quote",
        "component": "GravityAd",
        "variant": "minimal",
        "base_style": {
            "borderLeft": "3px solid #A1A1AA",
            "paddingLeft": 16,
        },
        "base_slot_props": {
            "inner": {"padding": "8px 0"},
            "text": {"fontStyle": "italic", "fontSize": 14, "color": "#52525B"},
            "label": {"fontSize": 9, "color": "#A1A1AA", "border": "none", "padding": 0},
        },
        "extra_props": {"showLabel": True},
        "code": """\
<GravityAd
  ad={ad}
  variant="minimal"
  showLabel={true}
  style={{
    borderLeft: '3px solid #A1A1AA',
    paddingLeft: 16,
  }}
  slotProps={{
    inner: { style: { padding: '8px 0' } },
    text: { style: { fontStyle: 'italic', fontSize: 14, color: '#52525B' } },
    label: { style: { fontSize: 9, color: '#A1A1AA', border: 'none', padding: 0 } },
  }}
/>""",
        "omits": ["title", "cta"],
    },
    "minimal": {
        "name": "minimal",
        "description": "Minimal text-only treatment with no decoration",
        "type": "minimal",
        "component": "GravityAd",
        "variant": "minimal",
        "base_style": {},
        "base_slot_props": {
            "label": {
                "fontSize": 9,
                "color": "#A1A1AA",
                "border": "none",
                "padding": 0,
            },
        },
        "extra_props": {"showLabel": True},
        "code": """\
<GravityAd
  ad={ad}
  variant="minimal"
  showLabel={true}
  slotProps={{
    label: {
      style: {
        fontSize: 9,
        color: '#A1A1AA',
        border: 'none',
        padding: 0,
      },
    },
  }}
/>""",
        "omits": ["cta"],
    },
    "footnote": {
        "name": "footnote",
        "description": "Small footnote-sized text ad for bottom of content",
        "type": "footnote",
        "component": "GravityAd",
        "variant": "minimal",
        "base_style": {},
        "base_slot_props": {
            "inner": {"padding": "4px 0"},
            "text": {"fontSize": 11, "color": "#A1A1AA"},
            "label": {"fontSize": 8, "color": "#D4D4D8", "border": "none", "padding": 0},
        },
        "extra_props": {"showLabel": True, "labelText": "Sponsored"},
        "code": """\
<GravityAd
  ad={ad}
  variant="minimal"
  showLabel={true}
  labelText="Sponsored"
  slotProps={{
    inner: { style: { padding: '4px 0' } },
    text: { style: { fontSize: 11, color: '#A1A1AA' } },
    label: { style: { fontSize: 8, color: '#D4D4D8', border: 'none', padding: 0 } },
  }}
/>""",
        "omits": ["title", "cta"],
    },
    "text-link": {
        "name": "text-link",
        "description": "Inline text link that reads like a natural recommendation",
        "type": "text-link",
        "component": "AdText",
        "variant": None,
        "base_style": {
            "color": "#2563EB",
            "textDecoration": "underline",
            "fontSize": "inherit",
            "cursor": "pointer",
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<AdText
  ad={ad}
  style={{
    color: '#2563EB',
    textDecoration: 'underline',
    fontSize: 'inherit',
    cursor: 'pointer',
  }}
/>""",
        "omits": ["title", "cta", "brandName", "favicon"],
    },
    "hyperlink": {
        "name": "hyperlink",
        "description": "Simple hyperlink — ad text as a clickable link with no styling",
        "type": "hyperlink",
        "component": "AdText",
        "variant": None,
        "base_style": {
            "color": "inherit",
            "textDecoration": "underline",
            "fontSize": "inherit",
        },
        "base_slot_props": {},
        "extra_props": {},
        "code": """\
<AdText
  ad={ad}
  style={{
    color: 'inherit',
    textDecoration: 'underline',
    fontSize: 'inherit',
  }}
/>""",
        "omits": ["title", "cta", "brandName", "favicon"],
    },
}
