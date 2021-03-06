import React from "react";
import PropTypes from "prop-types";
import { elementType } from "prop-types-extra";

import createChainedFunction from "../util/create-chained-function";

const propTypes = {
  href: PropTypes.string,
  onClick: PropTypes.func,
  onKeyDown: PropTypes.func,
  disabled: PropTypes.bool,
  role: PropTypes.string,
  tabIndex: PropTypes.oneOfType([PropTypes.number, PropTypes.string]),

  /**
   * this is sort of silly but needed for Button
   */
  as: elementType,
};

const defaultProps = {
  as: "a",
};

function isTrivialHref(href) {
  return !href || href.trim() === "#";
}

/**
 * There are situations due to browser quirks or Bootstrap CSS where
 * an anchor tag is needed, when semantically a button tag is the
 * better choice. SafeAnchor ensures that when an anchor is used like a
 * button its accessible. It also emulates input `disabled` behavior for
 * links, which is usually desirable for Buttons, NavItems, DropdownItems, etc.
 */
class SafeAnchor extends React.Component {
  constructor(props, context) {
    super(props, context);

    this.handleClick = this.handleClick.bind(this);
    this.handleKeyDown = this.handleKeyDown.bind(this);
  }

  handleClick(event) {
    const { disabled, href, onClick } = this.props;

    if (disabled || isTrivialHref(href)) {
      event.preventDefault();
    }

    if (disabled) {
      event.stopPropagation();
      return;
    }

    if (onClick) {
      onClick(event);
    }
  }

  handleKeyDown(event) {
    if (event.key === " ") {
      event.preventDefault();
      this.handleClick(event);
    }
  }

  render() {
    const {
      as: Component,
      disabled,
      onKeyDown,
      innerRef,
      ...props
    } = this.props;

    if (isTrivialHref(props.href)) {
      props.role = props.role || "button";
      // we want to make sure there is a href attribute on the node
      // otherwise, the cursor incorrectly styled (except with role='button')
      props.href = props.href || "#";
    }

    if (disabled) {
      props.tabIndex = -1;
      props["aria-disabled"] = true;
    }
    if (innerRef) props.ref = innerRef;
    return (
      <Component
        {...props}
        onClick={this.handleClick}
        onKeyDown={createChainedFunction(this.handleKeyDown, onKeyDown)}
      />
    );
  }
}

SafeAnchor.propTypes = propTypes;
SafeAnchor.defaultProps = defaultProps;

export default SafeAnchor;
